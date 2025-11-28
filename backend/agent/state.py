from typing import List, NotRequired, Literal, Any
from langgraph.graph import MessagesState
from langgraph.graph.message import AnyMessage
from copilotkit import CopilotKitState
class AgentState(CopilotKitState):
    user_id:NotRequired[str]
    model_name:NotRequired[str]
    messages: List[AnyMessage]
    intent: NotRequired[Literal["allowed", "blocked"]] 
    intent_reason: NotRequired[str]
    actions: NotRequired[List[Any]]
    