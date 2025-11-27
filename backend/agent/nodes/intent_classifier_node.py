
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent.nodes.helpers.prompt_helper import get_intent_prompt
from agent.nodes.helpers import query_validator

BLOCKED_MESSAGE = "Unauthorized use or prohibited keywords in the query."
MODE = "loose"

async def intent_classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages",[])
    if not messages:
       return {"intent":"allowed"}
   
    last_message = messages[-1]
    query = last_message.content.lower()
    is_valid_query = query_validator.validate_query(query)
    
    if not is_valid_query:
        return {
            "intent": "blocked",
            "intent_reason": BLOCKED_MESSAGE
        }
        
    try:
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_KEY")
        )
        human_message = get_intent_prompt(query)
        
        classification_messages = [
            SystemMessage(content="You are a banking security classifier"),
            HumanMessage(content = human_message)
        ]
        
        response = await llm.ainvoke(classification_messages)
        intent = response.content.strip().lower()
        
        if "blocked" in intent:
            final_intent = "blocked"
            reason = BLOCKED_MESSAGE
        else:
            final_intent = "allowed"
            reason = ""
        
        return {
            "intent": final_intent,
            "intent_reason": reason
        }
        

    except Exception as e:
        if MODE == "strict":
            return {"intent": "blocked", "intent_reason": "Error during classification"}
        else:
            return {"intent": "allowed", "intent_reason": ""}
    