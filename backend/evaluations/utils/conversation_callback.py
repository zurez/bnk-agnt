"""
Conversation callback for DeepEval ConversationSimulator.

This module provides the callback function that wraps the banking agent
for multi-turn conversation simulation.
"""

import uuid
from typing import List
from deepeval.test_case import Turn
from langchain_core.messages import HumanMessage, AIMessage
from bankbot.graph import graph
from evaluations.config import eval_config


async def banking_agent_callback(
    input: str,
    turns: List[Turn],
    thread_id: str
) -> Turn:
    """
    Callback function for ConversationSimulator.
    
    Converts deepeval Turn format to LangGraph messages,
    invokes the banking agent, and returns the response.
    
    Args:
        input: Current user input
        turns: Previous conversation turns
        thread_id: Conversation thread ID
        
    Returns:
        Turn object with assistant's response
    """
    # Convert previous turns to LangGraph messages
    messages = []
    for turn in turns:
        if turn.role == "user":
            messages.append(HumanMessage(content=turn.content))
        elif turn.role == "assistant":
            messages.append(AIMessage(content=turn.content))
    
    # Add current user input
    messages.append(HumanMessage(content=input))
    
    # Prepare agent state
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    
    state = {
        "messages": messages,
        "user_id": eval_config.test_user_id,
        "model_name": eval_config.evaluation_model,
        "openai_api_key": eval_config.openai_api_key,
    }
    
    # Invoke the agent
    try:
        result = await graph.ainvoke(state, config)
        
        # Extract the last assistant message
        last_message = result["messages"][-1]
        response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return Turn(role="assistant", content=response_content)
        
    except Exception as e:
        # Return error message as assistant response
        error_msg = f"I encountered an error: {str(e)}"
        return Turn(role="assistant", content=error_msg)


def create_model_callback_for_llm(model_name: str):
    """
    Create a callback function for a specific LLM model.
    
    This supports the "same prompt, different LLMs" comparison scenario.
    
    Args:
        model_name: Name of the LLM model to use
        
    Returns:
        Async callback function configured for the specified model
    """
    async def model_specific_callback(
        input: str,
        turns: List[Turn],
        thread_id: str
    ) -> Turn:
        """Callback with specific model configuration."""
        # Convert previous turns to LangGraph messages
        messages = []
        for turn in turns:
            if turn.role == "user":
                messages.append(HumanMessage(content=turn.content))
            elif turn.role == "assistant":
                messages.append(AIMessage(content=turn.content))
        
        # Add current user input
        messages.append(HumanMessage(content=input))
        
        # Prepare agent state with specific model
        config = {
            "configurable": {
                "thread_id": f"{thread_id}_{model_name}",  # Unique thread per model
            }
        }
        
        state = {
            "messages": messages,
            "user_id": eval_config.test_user_id,
            "model_name": model_name,
            "openai_api_key": eval_config.openai_api_key,
        }
        
        # Invoke the agent
        try:
            result = await graph.ainvoke(state, config)
            last_message = result["messages"][-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            return Turn(role="assistant", content=response_content)
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            return Turn(role="assistant", content=error_msg)
    
    return model_specific_callback
