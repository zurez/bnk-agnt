from mcp.mcp_tool import MCP_TOOL_NAMES
from typing import Any, Dict, List
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field




FRONTEND_TOOL_ALLOWLIST = {
    "showBalance",
    "showBeneficiaries",
    "showSpending",
    "showTransactions",
    "showTransferForm",
    "showPendingTransfers",
    "showAddBeneficiaryForm",
    "transferMoney",
}


class ShowBalanceInput(BaseModel):
    accounts: str = Field(
        description="JSON string of accounts array from get_balance tool. REQUIRED - you must pass the data you received from get_balance."
    )

class ShowBeneficiariesInput(BaseModel):
    beneficiaries: str = Field(
        description="JSON string of beneficiaries array from get_beneficiaries tool. REQUIRED."
    )

class ShowSpendingInput(BaseModel):
    spendingData: str = Field(
        description="JSON string of spending data array from get_spend_by_category tool. REQUIRED."
    )

class ShowTransactionsInput(BaseModel):
    transactions: str = Field(
        description="JSON string of transactions array from get_transactions tool. REQUIRED."
    )

class ShowTransferFormInput(BaseModel):
    accounts: str = Field(
        description="JSON string of accounts array from get_balance tool. REQUIRED."
    )
    beneficiaries: str = Field(
        description="JSON string of beneficiaries array from get_beneficiaries tool. REQUIRED."
    )

class ShowPendingTransfersInput(BaseModel):
    transfers: str = Field(
        description="JSON string of pending transfers array from get_pending_transfers tool. REQUIRED."
    )

FRONTEND_TOOL_SCHEMAS = {
    "showBalance": ShowBalanceInput,
    "showBeneficiaries": ShowBeneficiariesInput,
    "showSpending": ShowSpendingInput,
    "showTransactions": ShowTransactionsInput,
    "showTransferForm": ShowTransferFormInput,
    "showPendingTransfers": ShowPendingTransfersInput,
}

FRONTEND_TOOL_DESCRIPTIONS = {
    "showBalance": "Display account balances UI component. You MUST pass the accounts data from get_balance as a JSON string.",
    "showBeneficiaries": "Display beneficiaries list UI component. You MUST pass the beneficiaries data from get_beneficiaries as a JSON string.",
    "showSpending": "Display spending chart UI component. You MUST pass the spending data from get_spend_by_category as a JSON string.",
    "showTransactions": "Display transactions list UI component. You MUST pass the transactions data from get_transactions as a JSON string.",
    "showTransferForm": "Display transfer form UI component. You MUST pass accounts from get_balance AND beneficiaries from get_beneficiaries as JSON strings.",
    "showPendingTransfers": "Display pending transfers list UI component. You MUST pass the transfers data from get_pending_transfers as a JSON string.",
    "showAddBeneficiaryForm": "Display form to add a new beneficiary. Call this when user wants to add a beneficiary. No parameters needed.",
}


class ToolManager:
    """Manages frontend and backend tools for the agent."""
    
    def __init__(self, backend_tools: List[Any]):
        self.backend_tools = backend_tools
    
    def get_all_tools(self, state: Dict[str, Any]) -> List[Any]:
        """Get all tools (frontend + backend) for the agent."""
        frontend = self._create_frontend_tools(state)
        return frontend + self.backend_tools
    
    def _create_frontend_tools(self, state: Dict[str, Any]) -> List[StructuredTool]:
        """Extract frontend tools from CopilotKit state and convert to LangChain tools with proper schemas."""
        actions = state.get("copilotkit", {}).get("actions", [])
        tools, seen = [], set()
        
        for action in actions:
            name = action.get("name")
            if not name or name in seen or name not in FRONTEND_TOOL_ALLOWLIST:
                continue
            
            seen.add(name)
            
            schema = FRONTEND_TOOL_SCHEMAS.get(name)
            description = FRONTEND_TOOL_DESCRIPTIONS.get(name, action.get("description", f"Display {name} UI component"))
            
            if schema:
                tool = StructuredTool.from_function(
                    func=self._make_handler(name, schema),
                    name=name,
                    description=description,
                    args_schema=schema,
                )
            else:
                tool = StructuredTool.from_function(
                    func=self._make_handler(name),
                    name=name,
                    description=description,
                )
            
            tools.append(tool)
        
        return tools
    
    @staticmethod
    def _make_handler(name: str, schema: Any = None):
        def handler(**kwargs) -> str:
            if schema:
                try:
                    # Validate arguments against schema if provided
                    schema(**kwargs)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Invalid arguments for frontend tool {name}: {e}")
                    # We still return success as this is just a UI trigger, but logging helps debugging
            
            return f"UI component '{name}' displayed to user."
        return handler
    
    @staticmethod
    def has_backend_tools(tool_calls: List[Dict]) -> bool:
        """Check if any tool calls are backend tools."""
        return any(tc.get("name") in MCP_TOOL_NAMES for tc in tool_calls)