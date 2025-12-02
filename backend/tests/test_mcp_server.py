import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from mcp.mcp_impl import BankingMCPServer

@pytest.fixture
def mock_setup():
    with patch("mcp.mcp_impl.engine", new_callable=AsyncMock) as mock_eng:
        # Configure engine.connect() and engine.begin() to be MagicMock (not AsyncMock)
        # because they are not awaited, they return a context manager
        mock_conn = AsyncMock()
        
        # Create a mock that acts as an async context manager
        mock_ctx = MagicMock()
        mock_ctx.__aenter__.return_value = mock_conn
        mock_ctx.__aexit__.return_value = None
        
        mock_eng.connect = MagicMock(return_value=mock_ctx)
        mock_eng.begin = MagicMock(return_value=mock_ctx)
        
        server = BankingMCPServer()
        # Mock the session context manager
        mock_session_ctx = AsyncMock()
        server.SessionLocal = MagicMock(return_value=mock_session_ctx)
        
        yield {
            "server": server,
            "mock_conn": mock_conn,
            "mock_session_ctx": mock_session_ctx
        }

@pytest.mark.asyncio
async def test_get_balance(mock_setup):
    server = mock_setup["server"]
    mock_conn = mock_setup["mock_conn"]
    
    user_id = "test_user"
    
    # Mock result needs to be iterable
    row_mock = MagicMock()
    row_mock._mapping = {"account_id": "1", "name": "Savings", "balance": 1000.0, "currency": "USD"}
    
    mock_result = MagicMock()
    mock_result.__iter__.return_value = [row_mock]
    
    # Use side_effect to ensure return value is correct
    mock_conn.execute.side_effect = [mock_result]
    
    result = await server.get_balance(user_id)
    
    assert "accounts" in result
    assert len(result["accounts"]) == 1
    assert result["accounts"][0]["name"] == "Savings"
    assert result["accounts"][0]["balance"] == 1000.0

@pytest.mark.asyncio
async def test_get_transactions(mock_setup):
    server = mock_setup["server"]
    mock_conn = mock_setup["mock_conn"]
    
    user_id = "test_user"
    
    row_mock = MagicMock()
    row_mock._mapping = {"transaction_id": "t1", "amount": 50.0, "description": "Grocery", "date": datetime.now()}
    
    mock_result = MagicMock()
    mock_result.__iter__.return_value = [row_mock]
    
    mock_conn.execute.side_effect = [mock_result]
    
    result = await server.get_transactions(user_id, category="Food")
    
    assert len(result) == 1
    assert result[0]["amount"] == 50.0
    assert mock_conn.execute.called

@pytest.mark.asyncio
async def test_propose_transfer_insufficient_funds(mock_setup):
    server = mock_setup["server"]
    mock_conn = mock_setup["mock_conn"]
    
    user_id = "test_user"
    
    # Mock account lookup returning low balance
    mock_result_account = MagicMock()
    mock_result_account.first.return_value = MagicMock(balance=10.0)
    
    # Mock beneficiary lookup
    # propose_transfer uses engine.begin() -> conn.execute()
    # It executes:
    # 1. select(accounts) for from_account
    # 2. select(beneficiaries)
    # Wait, let's check the code order in mcp_impl.py
    # propose_transfer:
    #   async with engine.begin() as conn:
    #     result = await conn.execute(select(accounts)...)
    #     from_account = result.first()
    #     ...
    
    # So first call is account lookup
    
    mock_conn.execute.side_effect = [
        mock_result_account, 
    ]
    
    result = await server.propose_transfer(user_id, "Savings", "Mom", 100.0)
    
    assert "error" in result
    assert "Insufficient funds" in result["error"]

@pytest.mark.asyncio
async def test_add_beneficiary(mock_setup):
    server = mock_setup["server"]
    mock_session_ctx = mock_setup["mock_session_ctx"]
    
    user_id = "test_user"
    
    # Mock account check
    mock_result = MagicMock()
    mock_result.first.return_value = {"id": "acc1"}
    mock_session_ctx.execute.return_value = mock_result
    
    # add_beneficiary uses SessionLocal
    # async with self.SessionLocal() as session:
    #   session.add(...)
    #   await session.commit()
    
    # Use a valid account number from the hardcoded map
    valid_account = 'PDB-ALICE-001'
    
    result = await server.add_beneficiary(user_id, valid_account, "Friend")
    
    if not result.get("success"):
        print(f"DEBUG: add_beneficiary error: {result.get('error')}")
    
    assert "success" in result
    assert result["success"] is True
    assert mock_session_ctx.commit.called

@pytest.mark.asyncio
async def test_approve_transfer_not_found(mock_setup):
    server = mock_setup["server"]
    mock_conn = mock_setup["mock_conn"]
    
    user_id = "test_user"
    
    # Mock transfer lookup returning None
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_conn.execute.return_value = mock_result
    
    result = await server.approve_transfer(user_id, "trans1")
    
    assert "error" in result
    assert "Transfer not found" in result["error"]
