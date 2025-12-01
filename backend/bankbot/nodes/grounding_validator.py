
import re
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class GroundingValidator:
    """Validates that LLM responses are grounded in tool call results."""
    
    FINANCIAL_PATTERNS = {
        'currency_prefix': r'\b(?:AED|USD|EUR)\s*[\d,]+\.?\d*\b',
        'currency_suffix': r'\b[\d,]+\.?\d*\s*(?:AED|USD|EUR)\b',
        'account_balance': r'\b(?:balance|available|funds?)\b.{0,20}?[\d,]+\.?\d*\b',
        'transaction_amount': r'\b(?:transfer|sent|received|paid|spent|cost|charged)\b.{0,20}?[\d,]+\.?\d*\b',
    }
    
    def __init__(self):
        self.tool_results: Dict[str, Any] = {}
        self.grounded_values: Set[str] = set()
    
    def register_tool_result(self, tool_name: str, result: str):
        """Register tool results for grounding validation."""
        self.tool_results[tool_name] = result
        # Extract numeric values from tool results
        numbers = re.findall(r'[\d,]+\.?\d*', result)
        self.grounded_values.update(numbers)
        logger.debug(f"Registered tool result for {tool_name}, extracted {len(numbers)} numeric values")
    
    def validate_response(self, response: str) -> Dict[str, Any]:
        """Check if financial claims in response are grounded in tool results."""
        issues = []
        
        for pattern_name, pattern in self.FINANCIAL_PATTERNS.items():
            matches = re.findall(pattern, response, re.I)
            for match in matches:
                # Extract the numeric value
                numbers = re.findall(r'[\d,]+\.?\d*', match)
                for num in numbers:
                    normalized = num.replace(',', '')
                    if normalized and normalized not in self.grounded_values:
                        # Check if it's close to any grounded value (floating point tolerance)
                        if not self._is_close_to_grounded(normalized):
                            issues.append({
                                'type': 'ungrounded_financial_claim',
                                'pattern': pattern_name,
                                'value': match,
                                'severity': 'high'
                            })
        
        return {
            'is_grounded': len(issues) == 0,
            'issues': issues,
            'tool_calls_made': list(self.tool_results.keys()),
            'grounded_values_count': len(self.grounded_values)
        }
    
    def _is_close_to_grounded(self, value: str) -> bool:
        """Check if value is approximately equal to any grounded value."""
        try:
            val = float(value)
            for grounded in self.grounded_values:
                try:
                    grounded_val = float(grounded.replace(',', ''))
                    if abs(val - grounded_val) < 0.01:  # Tolerance for rounding
                        return True
                except ValueError:
                    continue
        except ValueError:
            pass
        return False
