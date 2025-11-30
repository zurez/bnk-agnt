import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from backend.mcp.mcp_tool import propose_transfer, propose_internal_transfer

@pytest.mark.asyncio
async def test_propose_transfer_amount_validation():
    # Mock settings
    with patch('backend.mcp.mcp_tool.settings') as mock_settings:
        mock_settings.max_transfer_amount = 10000.0
        
        # Test negative amount
        result = await propose_transfer("user1", "Account1", "Beneficiary1", -100)
        assert json.loads(result)["success"] is False
        assert "must be positive" in json.loads(result)["error"]
        
        # Test zero amount
        result = await propose_transfer("user1", "Account1", "Beneficiary1", 0)
        assert json.loads(result)["success"] is False
        assert "must be positive" in json.loads(result)["error"]
        
        # Test amount exceeding limit
        result = await propose_transfer("user1", "Account1", "Beneficiary1", 10001)
        assert json.loads(result)["success"] is False
        assert "exceeds maximum transfer limit" in json.loads(result)["error"]

@pytest.mark.asyncio
async def test_propose_internal_transfer_amount_validation():
    # Mock settings
    with patch('backend.mcp.mcp_tool.settings') as mock_settings:
        mock_settings.max_transfer_amount = 5000.0
        
        # Test negative amount
        result = await propose_internal_transfer("user1", "Account1", "Account2", -50)
        assert json.loads(result)["success"] is False
        assert "must be positive" in json.loads(result)["error"]
        
        # Test amount exceeding limit
        result = await propose_internal_transfer("user1", "Account1", "Account2", 6000)
        assert json.loads(result)["success"] is False
        assert "exceeds maximum transfer limit" in json.loads(result)["error"]
