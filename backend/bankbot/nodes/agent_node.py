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
from bankbot.nodes.grounding_validator import GroundingValidator
from config import settings
from bankbot.utils.agent_utils import validate_user_id, sanitize_msg, scrub_response, is_retryable
from bankbot.utils.llm_utils import get_llm


logger = logging.getLogger(__name__)

MAX_RETRIES = 3
tool_manager = ToolManager(backend_tools=MCP_TOOLS)



async def agent_node(state: AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name", "gpt-4o")
    messages = state.get("messages")
    
    if not messages:
        logger.warning(f"No messages for user {user_id}")
        return {"messages": [AIMessage(content="No input provided. Please send a message to start the conversation.")]}
    
    openai_key = state.get("openai_api_key")
    sambanova_key = state.get("sambanova_api_key")

    if settings.require_user_keys and not (openai_key or sambanova_key):
        return {"messages": [AIMessage(content="[SYSTEM_ERROR: MISSING_API_KEY]")]}
    
    llm = get_llm(model_name, openai_api_key=openai_key, sambanova_api_key=sambanova_key)
    tools = tool_manager.get_all_tools(state)
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
    
    validated_id = validate_user_id(user_id)
    system_msg = f"{get_system_prompt()}\n\nCurrent User ID: {validated_id}"
    
    clean_msgs = []
    for msg in messages:
        if getattr(msg, 'type', None) == 'human':
            clean_msgs.append(HumanMessage(content=sanitize_msg(msg.content)))
        else:
            clean_msgs.append(msg)
    
    history = [SystemMessage(content=system_msg)] + clean_msgs
    
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