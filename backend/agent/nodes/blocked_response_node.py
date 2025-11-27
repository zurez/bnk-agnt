from agent.state import AgentState
from langchain.messages import AIMessage

async def blocked_response_node(state: AgentState) -> AgentState:
   
    reason = state.get("intent_reason", "This request cannot be processed.")
    
    rejection_message = AIMessage(
        content=f"I apologize, but I cannot assist with this request. {reason}\n\n"
                f"I'm here to help with legitimate banking services such as:\n"
                f"- Checking your account balances\n"
                f"- Viewing your transaction history\n"
                f"- Analyzing your spending patterns\n"
                f"- Proposing transfers between your accounts\n\n"
                f"How else may I assist you today?"
    )
    
    state["messages"].append(rejection_message)
    return state
