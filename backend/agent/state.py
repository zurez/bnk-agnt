from typing import List, NotRequired, Literal
from langgraph.graph import MessagesState
from langgraph.graph.message import AnyMessage

class AgentState(MessagesState):
    user_id:NotRequired[str]
    model_name:NotRequired[str]
    messages: List[AnyMessage]
    intent: NotRequired[Literal["allowed", "blocked"]] 
    intent_reason: NotRequired[str]
    