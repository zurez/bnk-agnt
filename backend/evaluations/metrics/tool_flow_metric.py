"""
Custom metric for validating tool call sequences.

This metric checks if the agent called the expected sequence of tools
(both backend and frontend) to complete the user's request.
"""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from typing import List


class ToolFlowMetric(BaseMetric):
    """Validates that the agent called the expected sequence of tools."""
    
    def __init__(self, threshold: float = 0.8, strict_order: bool = False):
        """
        Initialize the ToolFlowMetric.
        
        Args:
            threshold: Minimum score required to pass (0.0 to 1.0)
            strict_order: If True, tools must be called in exact order.
                         If False, just checks that all required tools were called.
        """
        self.threshold = threshold
        self.strict_order = strict_order
        self.score = 0.0
        self.reason = ""
        self.success = False
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure the tool flow correctness.
        
        Returns:
            Score between 0.0 and 1.0
        """
        expected_flow = test_case.additional_metadata.get("expected_tool_flow", [])
        actual_tools = test_case.additional_metadata.get("actual_tool_calls", [])
        
        # If no expected flow specified, pass by default
        if not expected_flow:
            self.score = 1.0
            self.success = True
            self.reason = "No expected tool flow specified - test passed by default"
            return self.score
        
        # If no tools were called but some were expected
        if not actual_tools:
            self.score = 0.0
            self.success = False
            self.reason = f"No tools called. Expected: {' → '.join(expected_flow)}"
            return self.score
        
        if self.strict_order:
            # Check exact sequence match
            if actual_tools == expected_flow:
                self.score = 1.0
                self.success = True
                self.reason = f"Perfect match: {' → '.join(actual_tools)}"
            else:
                # Partial credit for having the right tools in wrong order
                missing = [t for t in expected_flow if t not in actual_tools]
                extra = [t for t in actual_tools if t not in expected_flow]
                
                if not missing and not extra:
                    self.score = 0.7  # Right tools, wrong order
                    self.success = self.score >= self.threshold
                    self.reason = f"Correct tools but wrong order. Expected: {' → '.join(expected_flow)}, Got: {' → '.join(actual_tools)}"
                else:
                    self.score = max(0.0, 1.0 - (len(missing) + len(extra)) / len(expected_flow))
                    self.success = self.score >= self.threshold
                    parts = []
                    if missing:
                        parts.append(f"Missing: {', '.join(missing)}")
                    if extra:
                        parts.append(f"Extra: {', '.join(extra)}")
                    self.reason = f"{'. '.join(parts)}. Expected: {' → '.join(expected_flow)}, Got: {' → '.join(actual_tools)}"
        else:
            # Just check that all required tools were called (order doesn't matter)
            missing = [t for t in expected_flow if t not in actual_tools]
            extra = [t for t in actual_tools if t not in expected_flow]
            
            if not missing and not extra:
                self.score = 1.0
                self.success = True
                self.reason = f"Perfect match: {' → '.join(actual_tools)}"
            elif not missing:
                # All required tools called, but some extra ones too
                self.score = 0.9
                self.success = self.score >= self.threshold
                self.reason = f"All required tools called. Extra tools: {', '.join(extra)}. Got: {' → '.join(actual_tools)}"
            else:
                # Some required tools missing
                matched = len([t for t in expected_flow if t in actual_tools])
                self.score = matched / len(expected_flow)
                self.success = self.score >= self.threshold
                self.reason = f"Missing tools: {', '.join(missing)}. Expected: {' → '.join(expected_flow)}, Got: {' → '.join(actual_tools)}"
        
        return self.score
    
    def is_successful(self) -> bool:
        """Check if the metric passed."""
        return self.success
    
    @property
    def __name__(self) -> str:
        """Metric name for display."""
        return "Tool Flow"
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async version of measure (required by BaseMetric)."""
        return self.measure(test_case)
