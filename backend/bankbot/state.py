from typing import List, Literal, Optional, Any, Annotated
from langgraph.graph.message import add_messages
from copilotkit import CopilotKitState

class AgentState(CopilotKitState):
    messages: Annotated[List[Any], add_messages]
    user_id: Optional[str]
    model_name: Optional[str]
    intent: Optional[Literal["allowed", "blocked"]]
    intent_reason: Optional[str]
    actions: Optional[List[Any]]