import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock copilotkit and langgraph to avoid import errors
sys.modules["copilotkit"] = MagicMock()
sys.modules["langgraph"] = MagicMock()
sys.modules["langgraph.graph"] = MagicMock()
sys.modules["langgraph.graph.graph"] = MagicMock()
sys.modules["langgraph.graph.message"] = MagicMock()
sys.modules["langchain_sambanova"] = MagicMock()

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from bankbot.nodes.agent_node import agent_node
from bankbot.state import AgentState

@pytest.fixture
def mock_dependencies():
    with patch("bankbot.nodes.agent_node.get_llm") as mock_get_llm, \
         patch("bankbot.nodes.agent_node.tool_manager") as mock_tool_manager, \
         patch("bankbot.nodes.agent_node.GroundingValidator") as mock_validator_cls, \
         patch("bankbot.nodes.agent_node.settings") as mock_settings:
        
        # Setup LLM mock
        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_get_llm.return_value = mock_llm
        
        # Setup async generator for astream
        async def async_gen(messages):
            yield AIMessage(content="Hello there!")
        mock_llm_with_tools.astream.side_effect = async_gen
        
        # Setup Validator mock
        mock_validator = MagicMock()
        mock_validator.validate_response.return_value = {'is_grounded': True, 'issues': []}
        mock_validator_cls.return_value = mock_validator
        
        # Setup Settings
        mock_settings.require_user_keys = False
        
        yield {
            "get_llm": mock_get_llm,
            "tool_manager": mock_tool_manager,
            "validator": mock_validator,
            "settings": mock_settings,
            "llm_with_tools": mock_llm_with_tools
        }

@pytest.mark.asyncio
async def test_agent_node_happy_path(mock_dependencies):
    state = {
        "user_id": "test_user",
        "messages": [HumanMessage(content="Hi")]
    }
    
    result = await agent_node(state)
    
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].content == "Hello there!"

@pytest.mark.asyncio
async def test_agent_node_missing_keys(mock_dependencies):
    mock_dependencies["settings"].require_user_keys = True
    
    state = {
        "user_id": "test_user",
        "messages": [HumanMessage(content="Hi")],
        "openai_api_key": None,
        "sambanova_api_key": None
    }
    
    result = await agent_node(state)
    
    assert "messages" in result
    assert "[SYSTEM_ERROR: MISSING_API_KEY]" in result["messages"][0].content

@pytest.mark.asyncio
async def test_agent_node_ungrounded_claims(mock_dependencies):
    # Setup validator to return ungrounded
    mock_dependencies["validator"].validate_response.return_value = {
        'is_grounded': False, 
        'issues': [{'type': 'ungrounded', 'value': '1000'}]
    }
    
    state = {
        "user_id": "test_user",
        "messages": [HumanMessage(content="Check balance")]
    }
    
    result = await agent_node(state)
    
    assert "Please verify these details" in result["messages"][0].content

@pytest.mark.asyncio
async def test_agent_node_llm_error_retry(mock_dependencies):
    # Mock astream to raise an exception then succeed (simulating retry would be complex, 
    # so let's just test the error handling for a persistent error or the retry logic if possible.
    # For simplicity in this unit test, let's test the "Service unavailable" fallback after retries)
    
    mock_llm_with_tools = mock_dependencies["llm_with_tools"]
    
    # Make it always fail
    async def async_gen_fail(messages):
        raise ValueError("429 Rate limit exceeded")
        yield # unreachable
        
    mock_llm_with_tools.astream.side_effect = async_gen_fail
    
    state = {
        "user_id": "test_user",
        "messages": [HumanMessage(content="Hi")]
    }
    
    # We expect it to retry a few times then return the error message
    # To speed up test, we can mock asyncio.sleep
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await agent_node(state)
    
    assert "messages" in result
    assert "temporarily unavailable" in result["messages"][0].content

@pytest.mark.asyncio
async def test_agent_node_sanitization(mock_dependencies):
    state = {
        "user_id": "test_user",
        "messages": [HumanMessage(content="Hi \x00 bad char")]
    }
    
    # We want to verify that the LLM is called with sanitized input
    # The agent_node calls sanitize_msg on human messages
    
    await agent_node(state)
    
    # Check the call args to astream
    call_args = mock_dependencies["llm_with_tools"].astream.call_args
    history = call_args[0][0]
    
    # history[0] is system message, history[1] is the human message
    assert "bad char" in history[1].content
    assert "\x00" not in history[1].content
