from typing import Dict

from langchain_openai import ChatOpenAI
from agent.state import AgentState
from langchain.agents import create_agent
from langchain_sambanova import ChatSambaNova
from agent.nodes.helpers.prompt_helper import get_system_prompt

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

# ToDo add model instantiator

async def agent_node(state:AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name","gpt-4o")
    context = {
        "user_id": user_id
    }
    system_message = system_message = f"{get_system_prompt()}\n\nCurrent User ID: {user_id}"

    if model_name in SAMBANOVA_MODELS:
        llm = ChatSambaNova(
            model=SAMBANOVA_MODELS[model_name],
            max_tokens=2048,
            temperature=0,
            top_p=0.01,
        )
        
    else:
        llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0,
        )
    agent = create_agent(
        model = llm,
        system_prompt= system_message,
        tools = [],
        name="agent"
    )
    
    result = await agent.ainvoke(state)
    return result