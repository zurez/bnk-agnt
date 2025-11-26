from backend.agent.state import AgentState


def should_continue(state: AgentState) -> str:
    intent = state.get("intent", "unknown")
    if intent == "blocked":
        return "end"
    return "agent"