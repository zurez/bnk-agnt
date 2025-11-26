from typing import Dict
from backend.agent.state import AgentState
from langchain.agents import create_agent


async def get_system_message(context:Dict):
    return "You are an agent"


async def agent_node(state:AgentState):
    user_id = state.get("user_id", "unknown")
    model_name = state.get("model_name","gpt-4o")
    context = {
        user_id
    }
    system_message = get_system_message(context)

    agent = create_agent(
        model = model_name,
        system_message = system_message,
        tools = []
    )
    
    result = await agent.ainvoke(state)
    return result