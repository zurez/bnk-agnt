
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from langchain_core.tools import tool
from pydantic import Field, field_validator
import json
import uuid
import math
from mcp.mcp_impl import BankingMCPServer
from config import settings


mcp_server = BankingMCPServer()

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def validate_amount(amount: float) -> Decimal:

    if not isinstance(amount, (int, float)):
        raise ValueError(f"Invalid amount type: {type(amount).__name__}. Expected int or float.")
    
    if math.isnan(amount):
        raise ValueError("Invalid amount value: NaN (Not a Number)")
    if math.isinf(amount):
        raise ValueError("Invalid amount value: Infinity")
    
    try:
        decimal_amount = Decimal(str(amount)).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Cannot convert amount to valid currency value: {e}")

    if decimal_amount <= 0:
        raise ValueError(f"Amount must be positive, got: {decimal_amount} AED")
    
    max_allowed = Decimal(str(settings.max_transfer_amount))
    if decimal_amount > max_allowed:
        raise ValueError(f"Amount {decimal_amount} AED exceeds maximum transfer limit of {max_allowed} AED")
    
    return decimal_amount

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
    limit: int = 10,
    offset: int = 0
) -> str:
    """
    Get transaction history with optional filters.
    
    Args:
        user_id: The user's ID
        from_date: Optional start date (YYYY-MM-DD)
        to_date: Optional end date (YYYY-MM-DD)
        category: Optional category filter (e.g., 'groceries', 'restaurants')
        limit: Maximum number of transactions to return (default 10)
        offset: Number of transactions to skip (default 0)
    """
    result = await mcp_server.get_transactions(user_id, from_date, to_date, category, limit, offset)
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
        amount: Amount to transfer in AED (must be positive and <= max limit)
        description: Optional transfer description
    
    Returns:
        Proposal details with proposal_id for approval
    """
    # Validate amount with comprehensive checks
    try:
        validated_amount = validate_amount(amount)
    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
    
    result = await mcp_server.propose_transfer(
        user_id, from_account_name, to_beneficiary_nickname, float(validated_amount), description
    )
    return json.dumps(result, default=custom_serializer)


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
        amount: Amount to transfer in AED (must be positive and <= max limit)
        description: Optional transfer description
    """
    # Validate amount with comprehensive checks
    try:
        validated_amount = validate_amount(amount)
    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
    
    result = await mcp_server.propose_internal_transfer(
        user_id, from_account_name, to_account_name, float(validated_amount), description
    )
    return json.dumps(result, default=custom_serializer)

@tool
async def approve_transfer(user_id: str, transfer_id: str) -> str:
    """
    Approve and execute a pending transfer.
    
    Args:
        user_id: The user's ID (must match transfer owner)
        transfer_id: The transfer/proposal ID to approve
    """
    result = await mcp_server.approve_transfer(user_id, transfer_id)
    return json.dumps(result, default=custom_serializer)

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
    return json.dumps(result, default=custom_serializer)


@tool
async def get_pending_transfers(user_id: str) -> str:
    """
    Get all pending transfers for a user that need approval.
    
    Args:
        user_id: The user's ID
    """
    result = await mcp_server.get_pending_transfers(user_id)
    return json.dumps(result, default=custom_serializer)


@tool
async def get_transfer_history(user_id: str, limit: int = 10) -> str:
    """
    Get transfer history for a user (completed, rejected, etc.)
    
    Args:
        user_id: The user's ID
        limit: Maximum transfers to return (default 10)
    """
    result = await mcp_server.get_transfer_history(user_id, limit)
    return json.dumps(result, default=custom_serializer)

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
    return json.dumps(result, default=custom_serializer)

@tool
async def add_beneficiary(
    user_id: str,
    account_number: str,
    nickname: str
) -> str:
    """
    Add a new beneficiary for the user. Only Phoenix Digital Bank accounts supported.
    
    Args:
        user_id: The user's ID
        account_number: Account number (e.g., PDB-ALICE-001, PDB-BOB-001, PDB-CAROL-001)
        nickname: Friendly name for this beneficiary
    """
    result = await mcp_server.add_beneficiary(user_id, account_number, nickname)
    return json.dumps(result, default=custom_serializer)

@tool
async def remove_beneficiary(user_id: str, beneficiary_id: str) -> str:
    """
    Remove a beneficiary from user's list.
    
    Args:
        user_id: The user's ID
        beneficiary_id: The beneficiary ID to remove
    """
    result = await mcp_server.remove_beneficiary(user_id, beneficiary_id)
    return json.dumps(result, default=custom_serializer)


MCP_TOOLS = [
    get_balance,
    get_transactions,
    get_spend_by_category,
    get_beneficiaries,
    add_beneficiary,
    remove_beneficiary,
    propose_transfer,
    propose_internal_transfer,
    approve_transfer,
    reject_transfer,
    get_pending_transfers,
    get_transfer_history,
]


MCP_TOOL_NAMES = {t.name for t in MCP_TOOLS}