from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    user_id: str
    model: Optional[str] = "gpt-4"