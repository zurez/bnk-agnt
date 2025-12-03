"""Shared models and enums for type safety and consistency."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TransferStatus(str, Enum):
    """Transfer status enum."""
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class TransactionType(str, Enum):
    """Transaction type enum."""
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"

# @todo - use it in the api error
class APIError(BaseModel):
    """Structured API error response."""
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")

# @todo - use it  
class APIResponse(BaseModel):
    """Structured API response wrapper."""
    success: bool
    error: Optional[APIError] = None
    data: Optional[dict] = None
