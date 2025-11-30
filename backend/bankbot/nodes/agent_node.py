
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


async def agent_node(state: AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name", "gpt-4o")
    
    llm = get_llm(model_name)
    all_tools = tool_manager.get_all_tools(state)
    
    llm_with_tools = llm.bind_tools(all_tools, parallel_tool_calls=False)
    
    system_message = f"{get_system_prompt()}\n\nCurrent User ID: {user_id}"
    history = [SystemMessage(content=system_message)] + list(state.get("messages") or [])
    
    for attempt in range(4):
        try:
            response = None
            async for chunk in llm_with_tools.astream(history):
                response = chunk if response is None else response + chunk
            
            return {"messages": [response]}
            
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                if attempt < 3:
                    await asyncio.sleep((2 ** attempt) + random.random())
                    continue
                return {"messages": [AIMessage(content="Too many requests. Please try again in a minute.")]}
            
            if "400" in error_msg:
                return {"messages": [AIMessage(content="I encountered an error. Please try again.")]}
            
            return {"messages": [AIMessage(content=f"Technical issue: {e}. Please try again.")]}