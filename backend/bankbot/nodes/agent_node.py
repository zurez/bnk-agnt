from langchain_core.messages.ai import AIMessage
from langchain_core.messages.system import SystemMessage
from typing import Dict

from langchain_openai import ChatOpenAI
from bankbot.state import AgentState
from langchain.agents import create_agent
from langchain_sambanova import ChatSambaNova
from bankbot.nodes.helpers.prompt_helper import get_system_prompt
from mcp.mcp_tool import get_balance, get_spend_by_category, get_transactions, propose_transfer, tool
from bankbot.tool_manager import ToolManager, FRONTEND_TOOL_ALLOWLIST
import logging
logger = logging.getLogger(__name__)


SAMBANOVA_MODELS = {
    "deepseek-r1": "DeepSeek-R1-0528",
    "deepseek-v3": "DeepSeek-V3-0324",
    "deepseek-v3.1": "DeepSeek-V3.1",
    "deepseek-r1-distill": "DeepSeek-R1-Distill-Llama-70B",
    "llama-3.3-70b": "Meta-Llama-3.3-70B-Instruct",
    "llama-3.1-8b": "Meta-Llama-3.1-8B-Instruct",
    "gpt-oss-120b": "gpt-oss-120b",
    "qwen3-32b": "Qwen3-32B",
}
MCP_TOOLS = [get_balance, get_transactions,
             get_spend_by_category, propose_transfer]

tool_manager = ToolManager(
    frontend_allowlist=FRONTEND_TOOL_ALLOWLIST,
    backend_tools=MCP_TOOLS,
    max_frontend_tools=50,
)

def adapt_frontend_tools(frontend_tools: list) -> list:
    """Convert CopilotKit frontend action dicts to LangChain-compatible format."""
    adapted = []
    for t in frontend_tools:
        # Skip if tool doesn't have a name
        if not t.get("name"):
            logger.warning(f"Skipping frontend tool without name: {t}")
            continue
            
        # Get parameters - CopilotKit sends "jsonSchema" key for parameters sometimes
        params = t.get("parameters") or t.get("jsonSchema")
        if isinstance(params, str):
            import json
            try:
                params = json.loads(params)
            except:
                params = {"type": "object", "properties": {}}
        elif not params:
            params = {"type": "object", "properties": {}}
        
        # Ensure params has required schema structure
        if isinstance(params, dict) and "type" not in params:
            params = {"type": "object", "properties": params}
        
        # Create a dict with 'title' and 'description' at top level for LangChain
        # This format is recognized by convert_to_openai_function
        tool_dict = {
            "title": t["name"],
            "description": t.get("description", ""),
            "type": "object",
            "properties": params.get("properties", {}),
        }
        
        # Add required fields if present
        if "required" in params:
            tool_dict["required"] = params["required"]
        
        adapted.append(tool_dict)
    return adapted

async def agent_node(state:AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name","gpt-4o")
    

    if model_name in SAMBANOVA_MODELS:
        # Check if this is a reasoning model
        is_reasoning_model = "r1" in model_name.lower()
        
        # Use different parameters for reasoning vs non-reasoning models
        if is_reasoning_model:
            llm_config = {
                "model": SAMBANOVA_MODELS[model_name],
                "max_tokens": 4096,  # R1 models need more tokens for reasoning
                "temperature": 0.6,  # Recommended for reasoning models
                "top_p": 0.95,  # Recommended for reasoning models
                "streaming": True,
            }
            logger.info(f"Using reasoning model: {model_name} with optimized parameters")
        else:
            llm_config = {
                "model": SAMBANOVA_MODELS[model_name],
                "max_tokens": 2048,
                "temperature": 0,
                "top_p": 0.01,
                "streaming": True,
            }
        
        llm = ChatSambaNova(**llm_config)
        
    else:
        llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0,
            streaming=True,  # Enable streaming for OpenAI models too
        )
    
    system_message_text = f"{get_system_prompt()}\n\nCurrent User ID: {user_id}"
    frontend_tools = tool_manager.gather_frontend_tools(state)
    
    logger.info(f"Frontend tools gathered: {len(frontend_tools)} tools")
    logger.debug(f"Frontend tools: {frontend_tools}")

    ftools = adapt_frontend_tools(frontend_tools)
    logger.info(f"Adapted frontend tools: {len(ftools)} tools")
    logger.debug(f"Adapted tools: {ftools}")
    
    all_tools = tool_manager.bind_to_model(llm, ftools)
    logger.info(f"Total tools to bind: {len(all_tools)} tools")
    
    # Log each tool's name for debugging
    for i, tool in enumerate(all_tools):
        if isinstance(tool, dict):
            name = tool.get("function", {}).get("name") if "function" in tool else tool.get("name")
            logger.debug(f"Tool {i}: {name} (dict)")
        else:
            name = getattr(tool, "name", "unknown")
            logger.debug(f"Tool {i}: {name} (object)")

    # Bind tools to the LLM - reasoning models CAN work with tool calling
    llm_with_tools = llm.bind_tools(all_tools, parallel_tool_calls=False)

    messages = list(state.get("messages") or [])

    history = [SystemMessage(content=system_message_text)] + messages
    
    import asyncio
    import random
    
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Invoking LLM: {model_name} (Attempt {attempt+1}/{max_retries+1})")
            
            # Use astream to ensure tokens are emitted immediately
            response_content = ""
            response_message = None
            
            async for chunk in llm_with_tools.astream(history):
                if response_message is None:
                    response_message = chunk
                else:
                    response_message += chunk
                    
            logger.info("LLM invocation successful")
            return {"messages": [response_message]}
            
        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "429" in error_msg or "rate_limit" in error_msg.lower()
            is_bad_request = "400" in error_msg or "bad_request" in error_msg.lower()
            
            # Handle Rate Limits (429)
            if is_rate_limit:
                if attempt < max_retries:
                    delay = (base_delay * (2 ** attempt)) + (random.random() * 1.0)
                    logger.warning(f"Rate limit hit. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} retries.")
                    return {"messages": [AIMessage(content="I'm currently receiving too many requests and reached my limit. Please try again in a minute.")]}
            
            # Handle Bad Request (400) - often malformed tool calls from reasoning models
            elif is_bad_request:
                logger.warning(f"Bad Request (likely malformed tool call): {error_msg}")
                # Try to extract the model output if available in the error message
                if "error_model_output" in error_msg:
                    try:
                        # Extract the output string from the error message if possible
                        # This is a hacky way to recover the text if the tool call failed
                        import re
                        match = re.search(r"'error_model_output':\s*'([^']*)'", error_msg)
                        if match:
                            recovered_text = match.group(1).replace("\\n", "\n")
                            logger.info("Recovered text from failed tool call error")
                            return {"messages": [AIMessage(content=f"I tried to perform an action but the format was incorrect. Here is what I intended:\n\n{recovered_text}")]}
                    except:
                        pass
                
                return {"messages": [AIMessage(content="I encountered an error formatting my response. Please try asking again.")]}
            
            # Handle other errors
            logger.error(f"Error invoking LLM: {error_msg}", exc_info=True)
            return {"messages": [AIMessage(content=f"I encountered a technical issue: {str(e)}. Please try again.")]}
    # agent = create_agent(
    #     model= llm,
    #     tools=all_tools,
    #     system_prompt=system_message
        
    # )
    # response = await agent.ainvoke(state)
    # new_messages = messages + [response if isinstance(response, AIMessage) else AIMessage(content=str(response))]
    # return {"messages": new_messages}