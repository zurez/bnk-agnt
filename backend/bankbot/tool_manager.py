from typing import Any, Dict, List
from langchain_core.tools import StructuredTool

MCP_TOOL_NAMES = {"get_balance", "get_transactions", "get_spend_by_category", "propose_transfer"}

FRONTEND_TOOL_ALLOWLIST = {"showBalance", "showBeneficiaries", "showTransfer", "showSpending", "transferMoney"}


class ToolManager:
    """Manages frontend and backend tools for the agent."""
    
    def __init__(self, backend_tools: List[Any]):
        self.backend_tools = backend_tools
    
    def get_all_tools(self, state: Dict[str, Any]) -> List[Any]:
        """Get all tools (frontend + backend) for the agent."""
        return self._create_frontend_tools(state) + self.backend_tools
    
    def _create_frontend_tools(self, state: Dict[str, Any]) -> List[StructuredTool]:
        """Extract frontend tools from CopilotKit state and convert to LangChain tools."""
        actions = state.get("copilotkit", {}).get("actions", [])
        tools, seen = [], set()
        
        for action in actions:
            name = action.get("name")
            if not name or name in seen or name not in FRONTEND_TOOL_ALLOWLIST:
                continue
            
            seen.add(name)
            tools.append(StructuredTool.from_function(
                func=self._make_handler(name),
                name=name,
                description=action.get("description", f"Display {name} UI"),
            ))
        
        return tools
    
    @staticmethod
    def _make_handler(name: str):
        def handler() -> str:
            return f"UI component '{name}' displayed."
        return handler
    
    @staticmethod
    def has_backend_tools(tool_calls: List[Dict]) -> bool:
        """Check if any tool calls are backend tools."""
        return any(tc.get("name") in MCP_TOOL_NAMES for tc in tool_calls)