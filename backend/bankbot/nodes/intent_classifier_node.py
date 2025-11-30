
import os
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_sambanova import ChatSambaNova
from langchain_core.messages import SystemMessage, HumanMessage

from bankbot.nodes.helpers.prompt_helper import get_intent_prompt
from bankbot.nodes.helpers import query_validator

logger = logging.getLogger(__name__)

BLOCKED_MESSAGE = "Unauthorized use or prohibited keywords in the query."
MODE = "loose"  # "strict" or "loose"


INTENT_CLASSIFIER_MODEL = "sambanova"  # "openai" or "sambanova"
SAMBANOVA_MODEL = "Meta-Llama-3.3-70B-Instruct"
OPENAI_MODEL = "gpt-4o-mini"


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
    
    logger.info(f"[INTENT_CLASSIFIER] Starting classification for query: '{query[:100]}...'")

    logger.info("[INTENT_CLASSIFIER] Step 1: Running rule-based validation")
    is_valid_query = query_validator.validate_query(query_lower)
    
    if not is_valid_query:
        logger.warning(f"[INTENT_CLASSIFIER] BLOCKED by rule-based validation")
        logger.warning(f"[INTENT_CLASSIFIER] Query: '{query}'")
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
    
    logger.info("[INTENT_CLASSIFIER] ✓ Passed rule-based validation")
      
    try:
        if INTENT_CLASSIFIER_MODEL == "sambanova":
            llm_name = f"SambaNova/{SAMBANOVA_MODEL}"
            logger.info(f"[INTENT_CLASSIFIER] Step 2: Using LLM classifier: {llm_name}")
            llm = ChatSambaNova(
                model=SAMBANOVA_MODEL,
                max_tokens=500,
                temperature=0,
            )
        else:
            llm_name = f"OpenAI/{OPENAI_MODEL}"
            logger.info(f"[INTENT_CLASSIFIER] Step 2: Using LLM classifier: {llm_name}")
            llm = ChatOpenAI(
                model=OPENAI_MODEL,
                temperature=0,
                api_key=os.getenv("OPENAI_KEY")
            )
        
     
        human_message = get_intent_prompt(query_lower)
        classification_messages = [
            SystemMessage(content="You are a banking security classifier"),
            HumanMessage(content=human_message)
        ]
        
        logger.info(f"[INTENT_CLASSIFIER] Invoking LLM with prompt length: {len(human_message)} chars")
        
        
        response = await llm.ainvoke(classification_messages)
        intent_response = response.content.strip().lower()
        
        logger.info(f"[INTENT_CLASSIFIER] LLM response: '{intent_response}'")
        
        if "blocked" in intent_response:
            final_intent = "blocked"
            reason = BLOCKED_MESSAGE
            logger.warning(f"[INTENT_CLASSIFIER] BLOCKED by LLM classifier")
            logger.warning(f"[INTENT_CLASSIFIER] LLM reasoning: '{intent_response}'")
        else:
            final_intent = "allowed"
            reason = ""
            logger.info(f"[INTENT_CLASSIFIER] ALLOWED by LLM classifier")
        
        return {
            "intent": final_intent,
            "intent_reason": reason,
            "classification_metadata": {
                "decision_method": "llm",
                "model": llm_name,
                "llm_response": intent_response,
                "query_snippet": query[:100],
                "result": final_intent,
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
            logger.info(f"[INTENT_CLASSIFIER] ALLOWED despite error (loose mode)")
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