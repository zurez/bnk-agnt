import re
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from backend.agent.nodes.helpers import query_validator
from backend.agent.nodes.helpers.prompt_helper import get_intent_prompt

BLOCKED_MESSAGE = "Unauthorized use or prohibited keywords in the query."
MODE = "loose"
async def intent_classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages",[])
    if not message:
        return state 
    last_message = messages[-1]
    query = last_message.content.lower()
    is_valid_query = query_validator(query)
    
    if not is_valid_query:
        state["intent"] = "blocked"
        state["intent_reason"] = BLOCKED_MESSAGE
        
    try:
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature=0
            api_key=os.getenv("OPENAI_KEY")
        )
        human_message = get_intent_prompt(query)
        
        classification_messages = [
            SystemMessage(content="You are a banking security classifier"),
            HumanMessage(content = human_message)
        ]
        
        response = await llm.ainvoke(classification_messages)
        intent = response.content.strip().lower()
        
        if intent == "blocked":
            state["intent"] = intent
            state["intent_reason"] = BLOCKED_MESSAGE
            return state
        
        state["intent"] = "allowed"
        state["intent_reason"]=""
        
        return state
    
    except Exception as e:
        if MODE == "strict":
            state["intent"] = "blocked"
        else:
            state["intent"] = "allowed"
        return state
        