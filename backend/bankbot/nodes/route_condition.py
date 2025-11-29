from langgraph.constants import END
from bankbot.state import AgentState
from bankbot.tool_manager import ToolManager


def should_continue(state: AgentState) -> str:
    intent = state.get("intent")
    return "end" if intent == "blocked" else "agent"


def route_tools(state: AgentState):
    """Route to tools node only for backend tools. Frontend tools end the graph."""
    last_message = state["messages"][-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return END
    
    has_backend = ToolManager.has_backend_tools(last_message.tool_calls)
    return "tools" if has_backend else END