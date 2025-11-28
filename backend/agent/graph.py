from agent.nodes.route_condition import should_continue
from agent.state import AgentState
from langgraph.graph import StateGraph, MessagesState, START, END

from agent.nodes.intent_classifier_node import intent_classifier_node
from agent.nodes.agent_node import agent_node
from agent.nodes.blocked_response_node import blocked_response_node
from langgraph.checkpoint.memory import MemorySaver


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
    workflow.add_edge("agent", END)
    workflow.add_edge("blocked_response", END)
    
    return workflow.compile(checkpointer=MemorySaver())

graph = create_agent_graph()