from typing import Any, Dict, List, Sequence, Optional
from langchain_core.language_models import BaseChatModel


MCP_TOOL_NAMES = {
    "get_balance",
    "get_transactions", 
    "get_spend_by_category",
    "propose_transfer"
}

# Frontend tools we allow the model to see
FRONTEND_TOOL_ALLOWLIST = {
    "showBalance",
    "showBeneficiaries",
    "showTransfer",
    "showSpending",
    "transferMoney",
}


class ToolManager:
    """Merge frontend tools with backend tools and detect frontend-only tool calls."""

    def __init__(
        self,
        *,
        frontend_allowlist: set[str],
        backend_tools: List[Any],
        max_frontend_tools: int = 50,
    ) -> None:
        self.frontend_allowlist = frontend_allowlist
        self.backend_tools = backend_tools
        self.max_frontend_tools = max_frontend_tools

    def gather_frontend_tools(self, state: Dict[str, Any]) -> List[Any]:
        """
        Read tools from state['actions'] (CopilotKit actions)
        and filter them by allowlist + dedupe by name.
        """
        raw_tools: List[Any] = []

        # Optional: other dynamic tools on state
        raw_tools.extend(state.get("tools", []) or [])

        # Copilot / frontend actions
        raw_actions = state.get("actions") or []
        if isinstance(raw_actions, list):
            raw_tools.extend(raw_actions)

        deduped: List[Any] = []
        seen: set[str] = set()
        for tool_candidate in raw_tools:
            name = self._extract_tool_name(tool_candidate)
            if not name:
                continue
            if name not in self.frontend_allowlist:
                continue
            if name in seen:
                continue
            seen.add(name)
            deduped.append(tool_candidate)

        return deduped[: self.max_frontend_tools]

    def bind_to_model(self, model: BaseChatModel, frontend_tools: List[Any]) -> List[Any]:
        """Combine frontend + backend tools into a single list."""
        all_tools = [*frontend_tools, *self.backend_tools]
        return all_tools

    @staticmethod
    def has_frontend_tool_calls(tool_calls: Sequence[Dict[str, Any]]) -> bool:
        """
        Returns True if any tool call is not a backend tool (i.e. must be handled by frontend).
        """
        for call in tool_calls:
            name = (call.get("name") or "").strip()
            if name and name not in MCP_TOOL_NAMES:
                return True
        return False

    @staticmethod
    def _extract_tool_name(tool: Any) -> Optional[str]:
        """
        Handle both dict-based tools (OpenAI-style) and objects with .name.
        """
        try:
            if isinstance(tool, dict):
                fn = tool.get("function") or {}
                if isinstance(fn, dict):
                    name = fn.get("name") or tool.get("name")
                else:
                    name = tool.get("name")
                return name.strip() if isinstance(name, str) else None
            name = getattr(tool, "name", None)
            return name.strip() if isinstance(name, str) else None
        except Exception:
            return None
