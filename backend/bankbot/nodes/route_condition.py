from langgraph.constants import END
from bankbot.state import AgentState
from bankbot.tool_manager import MCP_TOOL_NAMES

def should_continue(state: AgentState) -> str:
    intent = state.get("intent", "allowed")
    if intent == "blocked":
        return "end"
    return "agent"


def route_tools(state: AgentState):
    """
    Route to tools node only if there are backend (MCP) tools to execute.
    Frontend tools should end the graph so they can be sent to the frontend.
    """
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return END
    
    # Check if there are any backend tools to execute
    has_backend_tools = False
    for tool_call in last_message.tool_calls:
        if tool_call["name"] in MCP_TOOL_NAMES:
            has_backend_tools = True
            break
    
    # Only route to tools node if there are backend tools to execute
    # Frontend tools will be handled by the frontend via AG-UI protocol
    if has_backend_tools:
        return "tools"
    
    return END