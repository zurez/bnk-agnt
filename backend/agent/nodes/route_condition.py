from agent.state import AgentState


def should_continue(state: AgentState) -> str:
    intent = state.get("intent", "allowed")
    if intent == "blocked":
        return "end"
    return "agent"