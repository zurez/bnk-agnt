
from langchain_core.tools import tool

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
    to_account_name: str, 
    amount: float, 
    currency: str = "AED"
) -> str:
    """
    Propose a money transfer between user accounts (requires human approval).
    
    IMPORTANT: This only PROPOSES the transfer. It does NOT execute it.
    A human must approve the transfer in the UI.
    
    Args:
        user_id: The user's ID
        from_account_name: Name of source account (e.g., "Salary", "Savings")
        to_account_name: Name of destination account
        amount: Amount to transfer
        currency: Currency code (default: AED)
    
    Returns:
        Proposal details with proposal_id for approval tracking
    """
    result = await mcp_server.propose_transfer(
        user_id, from_account_name, to_account_name, amount, currency
    )
    return json.dumps(result, default=custom_serializer)


