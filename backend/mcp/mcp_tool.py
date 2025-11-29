
from datetime import datetime,date
from decimal import Decimal
from langchain_core.tools import tool
import json
import uuid
from mcp.mcp_impl import BankingMCPServer


mcp_server = BankingMCPServer()

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

@tool
async def get_balance(user_id: str) -> str:
    """Get account balances for a user. Returns list of accounts with balances."""

    result = await mcp_server.get_balance(user_id)
    return json.dumps(result, default=custom_serializer)

@tool
async def get_transactions(
    user_id: str, 
    from_date: str = None, 
    to_date: str = None, 
    category: str = None, 
    limit: int = 10
) -> str:
    """
    Get transaction history with optional filters.
    
    Args:
        user_id: The user's ID
        from_date: Optional start date (YYYY-MM-DD)
        to_date: Optional end date (YYYY-MM-DD)
        category: Optional category filter (e.g., 'groceries', 'restaurants')
        limit: Maximum number of transactions to return (default 10)
    """
    result = await mcp_server.get_transactions(user_id, from_date, to_date, category, limit)
    return json.dumps(result, default=custom_serializer)

@tool
async def get_spend_by_category(
    user_id: str, 
    from_date: str = None, 
    to_date: str = None
) -> str:
    """
    Aggregate spending by category for a user.
    
    Args:
        user_id: The user's ID
        from_date: Optional start date (YYYY-MM-DD)
        to_date: Optional end date (YYYY-MM-DD)
    
    Returns:
        List of dictionaries with category and total spending
    """
    result = await mcp_server.get_spend_by_category(user_id, from_date, to_date)
    return json.dumps(result, default=custom_serializer)

@tool
async def propose_transfer(
    user_id: str,
    from_account_name: str,
    to_beneficiary_nickname: str,
    amount: float,
    description: str = ""
) -> str:
    """
    Propose a money transfer to a beneficiary. Requires human approval.
    
    Args:
        user_id: The user's ID
        from_account_name: Source account name (e.g., "Salary Account", "Savings")
        to_beneficiary_nickname: Beneficiary nickname (e.g., "Bob - Main", "Carol - Current")
        amount: Amount to transfer in AED
        description: Optional transfer description
    
    Returns:
        Proposal details with proposal_id for approval
    """
    result = await mcp_server.propose_transfer(
        user_id, from_account_name, to_beneficiary_nickname, amount, description
    )
    return json.dumps(result, default=serialize)


@tool
async def propose_internal_transfer(
    user_id: str,
    from_account_name: str,
    to_account_name: str,
    amount: float,
    description: str = ""
) -> str:
    """
    Propose a transfer between user's own accounts. Requires human approval.
    
    Args:
        user_id: The user's ID
        from_account_name: Source account name (e.g., "Salary Account")
        to_account_name: Destination account name (e.g., "Savings Account")
        amount: Amount to transfer in AED
        description: Optional transfer description
    """
    result = await mcp_server.propose_internal_transfer(
        user_id, from_account_name, to_account_name, amount, description
    )
    return json.dumps(result, default=serialize)

@tool
async def approve_transfer(user_id: str, transfer_id: str) -> str:
    """
    Approve and execute a pending transfer.
    
    Args:
        user_id: The user's ID (must match transfer owner)
        transfer_id: The transfer/proposal ID to approve
    """
    result = await mcp_server.approve_transfer(user_id, transfer_id)
    return json.dumps(result, default=serialize)

@tool
async def reject_transfer(user_id: str, transfer_id: str, reason: str = "") -> str:
    """
    Reject a pending transfer.
    
    Args:
        user_id: The user's ID (must match transfer owner)
        transfer_id: The transfer/proposal ID to reject
        reason: Optional reason for rejection
    """
    result = await mcp_server.reject_transfer(user_id, transfer_id, reason)
    return json.dumps(result, default=serialize)


@tool
async def get_pending_transfers(user_id: str) -> str:
    """
    Get all pending transfers for a user that need approval.
    
    Args:
        user_id: The user's ID
    """
    result = await mcp_server.get_pending_transfers(user_id)
    return json.dumps(result, default=serialize)


@tool
async def get_transfer_history(user_id: str, limit: int = 10) -> str:
    """
    Get transfer history for a user (completed, rejected, etc.)
    
    Args:
        user_id: The user's ID
        limit: Maximum transfers to return (default 10)
    """
    result = await mcp_server.get_transfer_history(user_id, limit)
    return json.dumps(result, default=serialize)

@tool
async def get_beneficiaries(user_id: str) -> str:
    """
    Get list of beneficiaries for a user.
    
    Args:
        user_id: The user's ID
    
    Returns:
        List of beneficiaries with their details (nickname, account, bank)
    """
    result = await mcp_server.get_beneficiaries(user_id)
    return json.dumps(result, default=serialize)

@tool
async def add_beneficiary(
    user_id: str,
    beneficiary_account_number: str,
    nickname: str
) -> str:
    """
    Add a new beneficiary for the user. Only Phoenix Digital Bank accounts supported.
    
    Args:
        user_id: The user's ID
        beneficiary_account_number: Account number (e.g., PDB-ALICE-001, PDB-BOB-001, PDB-CAROL-001)
        nickname: Friendly name for this beneficiary
    """
    result = await mcp_server.add_beneficiary(user_id, beneficiary_account_number, nickname)
    return json.dumps(result, default=serialize)

@tool
async def remove_beneficiary(user_id: str, beneficiary_id: str) -> str:
    """
    Remove a beneficiary from user's list.
    
    Args:
        user_id: The user's ID
        beneficiary_id: The beneficiary ID to remove
    """
    result = await mcp_server.remove_beneficiary(user_id, beneficiary_id)
    return json.dumps(result, default=serialize)
