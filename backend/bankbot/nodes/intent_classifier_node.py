import os
import logging
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_openai import ChatOpenAI
from langchain_sambanova import ChatSambaNova
from langchain_core.messages import SystemMessage, HumanMessage

from config import settings
from bankbot.nodes.helpers.prompt_helper import get_intent_prompt
from bankbot.nodes.helpers import query_validator

logger = logging.getLogger(__name__)

BLOCKED_MESSAGE = "Unauthorized use or prohibited keywords in the query."
MODE = "loose"  # "strict" or "loose"


async def intent_classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:

    messages = state.get("messages", [])
    if not messages:
        logger.info("[INTENT_CLASSIFIER] No messages in state, allowing by default")
        return {
            "intent": "allowed",
            "classification_metadata": {
                "decision_method": "default",
                "reason": "No messages to classify"
            }
        }
   
    last_message = messages[-1]
    query = last_message.content
    query_lower = query.lower()
    
    is_valid = query_validator.validate_query(query)
    
    if not is_valid:
        logger.warning(f"[INTENT_CLASSIFIER] BLOCKED by rule-based validation: '{query}'")
        return {
            "intent": "blocked",
            "intent_reason": BLOCKED_MESSAGE,
            "classification_metadata": {
                "decision_method": "rule_based",
                "validator": "query_validator",
                "query_snippet": query[:100],
                "result": "blocked"
            }
        }
    
    try:
        if settings.intent_classifier_model_provider == "sambanova":
            llm_name = settings.intent_classifier_model
            llm = ChatSambaNova(
                model=settings.intent_classifier_model,
                max_tokens=100,
                temperature=0,
            )
        else:
            llm_name = settings.intent_classifier_model
            llm = ChatOpenAI(
                model=settings.intent_classifier_model,
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=100,
            )
        
     
        human_message = get_intent_prompt(query_lower)
        classification_messages = [
            SystemMessage(content="You are a banking security classifier"),
            HumanMessage(content=human_message)
        ]
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        async def invoke_with_retry(messages):
            return await llm.ainvoke(messages)

        response = await invoke_with_retry(classification_messages)
        intent_response = response.content.strip().lower()
        

        if "blocked" in intent_response:
            logger.warning(f"[INTENT_CLASSIFIER] BLOCKED by LLM: {intent_response}")
            return {
                "intent": "blocked",
                "intent_reason": BLOCKED_MESSAGE,
                "classification_metadata": {
                    "decision_method": "llm",
                    "model": llm_name,
                    "llm_response": intent_response,
                    "query_snippet": query[:100],
                    "result": "blocked",
                    "passed_rule_validation": True
                }
            }
        else:
            return {
                "intent": "allowed",
                "intent_reason": "",
                "classification_metadata": {
                    "decision_method": "llm",
                    "model": llm_name,
                    "llm_response": intent_response,
                    "query_snippet": query[:100],
                    "result": "allowed",
                    "passed_rule_validation": True
                }
            }
        

    except Exception as e:
        logger.error(f"[INTENT_CLASSIFIER]  Error during LLM classification: {str(e)}")
        logger.error(f"[INTENT_CLASSIFIER] Error type: {type(e).__name__}")
        
        if MODE == "strict":
            logger.warning(f"[INTENT_CLASSIFIER]  BLOCKED due to error (strict mode)")
            return {
                "intent": "blocked",
                "intent_reason": "Error during classification",
                "classification_metadata": {
                    "decision_method": "error_fallback",
                    "mode": MODE,
                    "error": str(e),
                    "result": "blocked"
                }
            }
        else:
            # Loose mode: allow despite error
            return {
                "intent": "allowed",
                "intent_reason": "",
                "classification_metadata": {
                    "decision_method": "error_fallback",
                    "mode": MODE,
                    "error": str(e),
                    "result": "allowed"
                }
            }