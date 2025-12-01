import re
import logging
import asyncio
import random

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_openai import ChatOpenAI

from bankbot.state import AgentState
from bankbot.nodes.helpers.prompt_helper import get_system_prompt
from mcp.mcp_tool import MCP_TOOLS
from bankbot.tool_manager import ToolManager
from langchain_sambanova import ChatSambaNova
from bankbot.nodes.grounding_validator import GroundingValidator


logger = logging.getLogger(__name__)

SAMBANOVA_MODELS = {
    "deepseek-r1": "DeepSeek-R1-0528",
    "deepseek-v3": "DeepSeek-V3-0324",
    "deepseek-v3.1": "DeepSeek-V3.1",
    "deepseek-r1-distill": "DeepSeek-R1-Distill-Llama-70B",
    "llama-3.3-70b": "Meta-Llama-3.3-70B-Instruct",
    "llama-3.1-8b": "Meta-Llama-3.1-8B-Instruct",
    "qwen3-32b": "Qwen3-32B",
}

MAX_RETRIES = 3
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$', re.I)

# stuff we really dont want leaking out
SYSTEM_PROMPT_MARKERS = [
    "critical: how to use tools",
    "current user id:",
    "backend tools",
    "frontend tools"
]

tool_manager = ToolManager(backend_tools=MCP_TOOLS)


def validate_user_id(user_id: str) -> str:
    if not UUID_PATTERN.match(user_id):
        logger.warning(f"Invalid UUID: {user_id[:20]}...")
        return "invalid"
    return user_id


def sanitize_msg(text: str) -> str:
    if not text or not isinstance(text, str):
        return "[Empty message]"
    
    # strip control chars and cap length
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)[:2000].strip()
    return cleaned or "[Empty message]"


def scrub_response(response: AIMessage) -> AIMessage:
    """Clean up LLM output before showing to user."""
    content = response.content
    
    # check for accidental system prompt regurgitation
    content_lower = content.lower()
    if any(marker in content_lower for marker in SYSTEM_PROMPT_MARKERS):
        logger.warning("System prompt leakage detected, blocking response")
        return AIMessage(content="I apologize, but I encountered an error. Please try again.")
    
    # basic XSS scrubbing (belt and suspenders)
    content = re.sub(r'<script|javascript:|on\w+\s*=', '', content, flags=re.I)
    
    return AIMessage(content=content, tool_calls=response.tool_calls)


def get_llm(model_name: str):
    if model_name not in SAMBANOVA_MODELS:
        return ChatOpenAI(model="gpt-4-turbo", temperature=0, streaming=True)
    
    # reasoning models need more room to think
    is_reasoning = "r1" in model_name.lower()
    return ChatSambaNova(
        model=SAMBANOVA_MODELS[model_name],
        max_tokens=4096 if is_reasoning else 2048,
        temperature=0.6 if is_reasoning else 0,
        top_p=0.95 if is_reasoning else 0.01,
        streaming=True,
    )


def is_retryable(err_msg: str) -> bool:
    """Rate limits, server errors, network hiccups - worth retrying."""
    err = err_msg.lower()
    return any(x in err for x in ["429", "rate_limit", "500", "503", "timeout", "connection", "network"])


async def agent_node(state: AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name", "gpt-4o")
    messages = state.get("messages")
    
    if not messages:
        logger.warning(f"No messages for user {user_id}")
        return {"messages": [AIMessage(content="No input provided. Please send a message to start the conversation.")]}
    
    llm = get_llm(model_name)
    tools = tool_manager.get_all_tools(state)
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
    
    validated_id = validate_user_id(user_id)
    system_msg = f"{get_system_prompt()}\n\nCurrent User ID: {validated_id}"
    
    # sanitize human messages, pass thru everything else
    clean_msgs = []
    for msg in messages:
        if getattr(msg, 'type', None) == 'human':
            clean_msgs.append(HumanMessage(content=sanitize_msg(msg.content)))
        else:
            clean_msgs.append(msg)
    
    history = [SystemMessage(content=system_msg)] + clean_msgs
    
    # track what the LLM should actualy know from tool calls
    grounding = GroundingValidator()
    for msg in messages:
        if isinstance(msg, ToolMessage):
            grounding.register_tool_result(msg.name, msg.content)
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = None
            async for chunk in llm_with_tools.astream(history):
                try:
                    response = chunk if response is None else response + chunk
                except TypeError:
                    # sometimes chunks dont add nicely, just take the latest
                    response = chunk

            if response is None:
                logger.error("LLM returned nothing")
                return {"messages": [AIMessage(content="I'm having trouble generating a response. Please try again.")]}
            
            response = scrub_response(response)
            
            # flag ungrounded financial claims
            if response.content:
                check = grounding.validate_response(response.content)
                if not check['is_grounded']:
                    logger.warning(f"Ungrounded claims: {check['issues']}")
                    response.content += "\n\n*Please verify these details by checking your account.*"
            
            return {"messages": [response]}
            
        except Exception as e:
            err = str(e)
            logger.warning(f"Agent error (attempt {attempt + 1}): {err}")
            
            if is_retryable(err) and attempt < MAX_RETRIES:
                wait = (2 ** attempt) + random.random()
                logger.info(f"Retrying in {wait:.1f}s...")
                await asyncio.sleep(wait)
                continue
            
            if is_retryable(err):
                return {"messages": [AIMessage(content="The service is temporarily unavailable. Please try again in a moment.")]}
            
            if "400" in err:
                return {"messages": [AIMessage(content="I encountered an error processing your request. Please try rephrasing.")]}
            
            logger.error(f"Unhandled {type(e).__name__} for user {user_id[:8]}...")
            return {"messages": [AIMessage(content="I encountered a technical issue processing your request. Please try again later.")]}