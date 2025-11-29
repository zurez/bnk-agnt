from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from bankbot.state import AgentState
from bankbot.nodes.intent_classifier_node import intent_classifier_node
from bankbot.nodes.agent_node import agent_node
from bankbot.nodes.blocked_response_node import blocked_response_node
from bankbot.nodes.route_condition import route_tools, should_continue

from mcp.mcp_tool import (
    get_balance,
    get_transactions,
    get_spend_by_category,
    get_beneficiaries,
    add_beneficiary,
    remove_beneficiary,
    propose_transfer,
    propose_internal_transfer,
    approve_transfer,
    reject_transfer,
    get_pending_transfers,
    get_transfer_history,
)

MCP_TOOLS = [
    get_balance,
    get_transactions,
    get_spend_by_category,
    get_beneficiaries,
    add_beneficiary,
    remove_beneficiary,
    propose_transfer,
    propose_internal_transfer,
    approve_transfer,
    reject_transfer,
    get_pending_transfers,
    get_transfer_history,
]


def create_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(MCP_TOOLS))
    workflow.add_node("blocked_response", blocked_response_node)
    workflow.add_edge(START, "intent_classifier")

    workflow.add_conditional_edges(
        "intent_classifier",
        should_continue,
        {"agent": "agent", "end": "blocked_response"}
    )
    
    workflow.add_conditional_edges(
        "agent",
        route_tools,
        {"tools": "tools", END: END}
    )
    
    workflow.add_edge("tools", "agent")
    workflow.add_edge("blocked_response", END)
    
    return workflow.compile(checkpointer=MemorySaver())


graph = create_agent_graph()