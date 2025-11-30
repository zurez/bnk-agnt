
import asyncio
import random
import logging

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_sambanova import ChatSambaNova

from bankbot.state import AgentState
from bankbot.nodes.helpers.prompt_helper import get_system_prompt
from bankbot.tool_manager import ToolManager
from mcp.mcp_tool import MCP_TOOLS


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

tool_manager = ToolManager(backend_tools=MCP_TOOLS)


def get_llm(model_name: str):
    if model_name not in SAMBANOVA_MODELS:
        return ChatOpenAI(model="gpt-4-turbo", temperature=0, streaming=True)
    
    is_reasoning = "r1" in model_name.lower()
    return ChatSambaNova(
        model=SAMBANOVA_MODELS[model_name],
        max_tokens=4096 if is_reasoning else 2048,
        temperature=0.6 if is_reasoning else 0,
        top_p=0.95 if is_reasoning else 0.01,
        streaming=True,
    )


def _is_retryable_error(error_msg: str) -> bool:
       
    retryable_patterns = [
        "429", "rate_limit",  
        "500", "503",    
        "timeout", "connection", "network"  
    ]
    error_lower = error_msg.lower()
    return any(pattern in error_lower for pattern in retryable_patterns)


async def agent_node(state: AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name", "gpt-4o")
    
    messages = state.get("messages")
    if not messages:
        logger.warning(f"No messages provided for user {user_id}")
        return {"messages": [AIMessage(content="No input provided. Please send a message to start the conversation.")]}
    
    llm = get_llm(model_name)
    all_tools = tool_manager.get_all_tools(state)
    
    llm_with_tools = llm.bind_tools(all_tools, parallel_tool_calls=False)
    
    system_message = f"{get_system_prompt()}\n\nCurrent User ID: {user_id}"
    history = [SystemMessage(content=system_message)] + list(messages)
    

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = None
            async for chunk in llm_with_tools.astream(history):
              
                try:
                    response = chunk if response is None else response + chunk
                except TypeError as te:
                    logger.error(f"Chunk accumulation failed: {te}. Chunk type: {type(chunk)}")
                    response = chunk

            if response is None:
                logger.error("LLM stream yielded no chunks")
                return {"messages": [AIMessage(content="I'm having trouble generating a response. Please try again.")]}
            
            return {"messages": [response]}
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Agent node error (attempt {attempt + 1}/{MAX_RETRIES + 1}): {error_msg}")
            
            if _is_retryable_error(error_msg):
                if attempt < MAX_RETRIES:
                    backoff_time = (2 ** attempt) + random.random()
                    logger.info(f"Retrying after {backoff_time:.2f}s...")
                    await asyncio.sleep(backoff_time)
                    continue
                return {"messages": [AIMessage(content="The service is temporarily unavailable. Please try again in a moment.")]}

            if "400" in error_msg:
                return {"messages": [AIMessage(content="I encountered an error processing your request. Please try rephrasing.")]}
            

            error_type = type(e).__name__
            logger.error(f"Unhandled error in agent_node for user {user_id[:8]}...: {error_type}")
            
            return {"messages": [AIMessage(content="I encountered a technical issue processing your request. Please try again later.")]}
