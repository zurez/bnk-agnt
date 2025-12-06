"""
Single-turn golden datasets for banking scenarios.

These datasets are used for evaluating individual agent responses
and follow the exact tool flows from prompt_helper.py:
1. Backend tool (fetch data) → Frontend tool (display UI)

Tool Flows:
- Balance: get_balance → showBalance
- Transactions: get_transactions → showTransactions
- Spending: get_spend_by_category → showSpending
- Beneficiaries: get_beneficiaries → showBeneficiaries
- Transfer: get_balance + get_beneficiaries → showTransferForm
- Add Beneficiary: showAddBeneficiaryForm (no backend first)
- Pending: get_pending_transfers → showPendingTransfers
"""

from deepeval.dataset import Golden


# Balance Inquiry - Flow: get_balance → showBalance
BALANCE_INQUIRY_GOLDENS = [
    Golden(
        input="What's my account balance?",
        expected_output="I've displayed your account balances above.",
        context=["User wants to check all account balances"],
        additional_metadata={
            "expected_tool_flow": ["get_balance", "showBalance"],
            "category": "balance_inquiry"
        }
    ),
    Golden(
        input="How much money do I have?",
        expected_output="Your account balances are shown above.",
        context=["User wants to see all balances"],
        additional_metadata={
            "expected_tool_flow": ["get_balance", "showBalance"],
            "category": "balance_inquiry"
        }
    ),
]

# Transaction History - Flow: get_transactions → showTransactions
TRANSACTION_HISTORY_GOLDENS = [
    Golden(
        input="Show me my recent transactions",
        expected_output="Here are your recent transactions.",
        context=["User wants to see transaction history"],
        additional_metadata={
            "expected_tool_flow": ["get_transactions", "showTransactions"],
            "category": "transaction_history"
        }
    ),
    Golden(
        input="What were my last 5 transactions?",
        expected_output="Here are your recent transactions.",
        context=["User wants limited transaction history"],
        additional_metadata={
            "expected_tool_flow": ["get_transactions", "showTransactions"],
            "category": "transaction_history"
        }
    ),
]

# Spending Analysis - Flow: get_spend_by_category → showSpending
SPENDING_ANALYSIS_GOLDENS = [
    Golden(
        input="Show me my spending breakdown",
        expected_output="Here's your spending breakdown by category.",
        context=["User wants spending analysis"],
        additional_metadata={
            "expected_tool_flow": ["get_spend_by_category", "showSpending"],
            "category": "spending_analysis"
        }
    ),
    Golden(
        input="How much have I spent this month?",
        expected_output="Your spending breakdown is shown above.",
        context=["User wants monthly spending summary"],
        additional_metadata={
            "expected_tool_flow": ["get_spend_by_category", "showSpending"],
            "category": "spending_analysis"
        }
    ),
]

# Beneficiary Management - Flow: get_beneficiaries → showBeneficiaries
BENEFICIARY_GOLDENS = [
    Golden(
        input="Who are my saved beneficiaries?",
        expected_output="Here are your saved beneficiaries.",
        context=["User wants to view beneficiaries"],
        additional_metadata={
            "expected_tool_flow": ["get_beneficiaries", "showBeneficiaries"],
            "category": "beneficiary_management"
        }
    ),
    Golden(
        input="I want to add a new beneficiary",
        expected_output="Please fill out the form to add a new beneficiary.",
        context=["User wants to add beneficiary - direct to form"],
        additional_metadata={
            "expected_tool_flow": ["showAddBeneficiaryForm"],
            "category": "beneficiary_management"
        }
    ),
]

# Transfer - Flow: get_balance + get_beneficiaries → showTransferForm
TRANSFER_GOLDENS = [
    Golden(
        input="I want to transfer money",
        expected_output="Please use the transfer form above to set up your transfer.",
        context=["User wants to initiate transfer - needs accounts and beneficiaries"],
        additional_metadata={
            "expected_tool_flow": ["get_balance", "get_beneficiaries", "showTransferForm"],
            "category": "transfer"
        }
    ),
    Golden(
        input="Show me my pending transfers",
        expected_output="Here are your pending transfers awaiting approval.",
        context=["User wants to view pending transfers"],
        additional_metadata={
            "expected_tool_flow": ["get_pending_transfers", "showPendingTransfers"],
            "category": "transfer"
        }
    ),
]

# All single-turn goldens combined
ALL_SINGLE_TURN_GOLDENS = (
    BALANCE_INQUIRY_GOLDENS +
    TRANSACTION_HISTORY_GOLDENS +
    SPENDING_ANALYSIS_GOLDENS +
    BENEFICIARY_GOLDENS +
    TRANSFER_GOLDENS
)

