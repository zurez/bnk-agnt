import re
import logging
from langchain_core.messages import AIMessage
from config import settings

logger = logging.getLogger(__name__)

UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$', re.I)

# stuff we really dont want leaking out
SYSTEM_PROMPT_MARKERS = [
    "critical: how to use tools",
    "current user id:",
    "backend tools",
    "frontend tools"
]

def validate_user_id(user_id: str) -> str:
    if not UUID_PATTERN.match(user_id):
        logger.warning(f"Invalid UUID: {user_id[:20]}...")
        return "invalid"
    return user_id


def sanitize_msg(text: str) -> str:
    if not text or not isinstance(text, str):
        return "[Empty message]"
     
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)[:settings.max_message_length].strip()
    return cleaned or "[Empty message]"


def scrub_response(response: AIMessage) -> AIMessage:
    content = response.content

    content_lower = content.lower()
    if any(marker in content_lower for marker in SYSTEM_PROMPT_MARKERS):
        logger.warning("System prompt leakage detected, blocking response")
        return AIMessage(content="I apologize, but I encountered an error. Please try again.")
    
    
    content = re.sub(r'<script|javascript:|on\w+\s*=', '', content, flags=re.I)
    
    return AIMessage(content=content, tool_calls=response.tool_calls)


def is_retryable(err_msg: str) -> bool:
    err = err_msg.lower()
    return any(x in err for x in ["429", "rate_limit", "500", "503", "timeout", "connection", "network"])
