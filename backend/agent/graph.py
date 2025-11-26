from backend.agent.nodes.route_condition import should_continue
from backend.agent.state import AgentState
from langgraph.graph import StateGraph, MessagesState, START, END

def create_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("blocked_response", blocked_response_node)
    
    workflow.add_edge(START, "intent_classifier")
    workflow.add_conditional_edges(
        "intent_classifier",
        should_continue,
        {
            "agent": "agent",
            "end": "blocked_response"
        }
    )
    
    pass