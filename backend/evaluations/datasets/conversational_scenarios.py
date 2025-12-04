"""
Conversational golden datasets for multi-turn evaluation.

These scenarios support testing complex workflows and conversation quality.
Can be used with ConversationSimulator for automated testing.
"""

from deepeval.dataset import ConversationalGolden


# Complex Transfer Workflow Scenarios
TRANSFER_WORKFLOW_SCENARIOS = [
    ConversationalGolden(
        scenario="User wants to transfer $500 to Bob but doesn't have Bob as a beneficiary yet",
        expected_outcome="User successfully adds Bob as beneficiary and completes the transfer",
        user_description="Alice, a regular banking customer who is tech-savvy",
        additional_metadata={
            "from_account": "Checking",
            "to_user": "Bob",
            "amount": 500,
            "expected_flow": ["check_balance", "add_beneficiary", "propose_transfer", "approve_transfer"]
        }
    ),
    ConversationalGolden(
        scenario="User wants to transfer money between their own accounts",
        expected_outcome="User successfully transfers money from Checking to Savings",
        user_description="Alice, wants to move $1000 to savings",
        additional_metadata={
            "from_account": "Checking",
            "to_account": "Savings",
            "amount": 1000,
            "expected_flow": ["get_balance", "propose_internal_transfer", "approve_transfer"]
        }
    ),
    ConversationalGolden(
        scenario="User tries to transfer more money than they have",
        expected_outcome="Agent politely informs user of insufficient funds and suggests checking balance",
        user_description="Alice, attempting to transfer $10000 but only has $5000",
        additional_metadata={
            "from_account": "Checking",
            "amount": 10000,
            "expected_flow": ["get_balance", "propose_transfer", "error_handling"]
        }
    ),
]

# Spending Analysis Conversation Scenarios
SPENDING_ANALYSIS_SCENARIOS = [
    ConversationalGolden(
        scenario="User wants to understand their spending patterns and drill down into specific categories",
        expected_outcome="User gets comprehensive spending breakdown and insights into grocery spending",
        user_description="Alice, concerned about monthly expenses",
        additional_metadata={
            "expected_flow": ["get_spend_by_category", "drill_down_category", "compare_periods"]
        }
    ),
    ConversationalGolden(
        scenario="User wants to compare spending across different time periods",
        expected_outcome="User successfully compares current month vs last month spending",
        user_description="Alice, budget-conscious user",
        additional_metadata={
            "expected_flow": ["get_spend_by_category", "get_transactions", "analysis"]
        }
    ),
]

# Account Management Dialogue Scenarios
ACCOUNT_MANAGEMENT_SCENARIOS = [
    ConversationalGolden(
        scenario="User wants to review recent transactions and understand a specific charge",
        expected_outcome="User finds the transaction and gets clarification",
        user_description="Alice, confused about a recent charge",
        additional_metadata={
            "expected_flow": ["get_transactions", "filter_transactions", "explain_transaction"]
        }
    ),
    ConversationalGolden(
        scenario="User wants comprehensive account overview including balances, recent activity, and spending",
        expected_outcome="User gets complete financial snapshot",
        user_description="Alice, doing monthly financial review",
        additional_metadata={
            "expected_flow": ["get_balance", "get_transactions", "get_spend_by_category"]
        }
    ),
]

# Customer Support Scenarios (Different User Personas)
CUSTOMER_SUPPORT_SCENARIOS = [
    ConversationalGolden(
        scenario="Frustrated user who can't find their pending transfer",
        expected_outcome="Agent calmly helps user locate and manage pending transfers",
        user_description="Alice, frustrated and impatient",
        additional_metadata={
            "user_emotion": "frustrated",
            "expected_flow": ["get_pending_transfers", "explain_status", "resolve_issue"]
        }
    ),
    ConversationalGolden(
        scenario="Confused user who is new to online banking",
        expected_outcome="Agent patiently guides user through basic operations",
        user_description="Alice, new to online banking, needs hand-holding",
        additional_metadata={
            "user_emotion": "confused",
            "expected_flow": ["explain_features", "get_balance", "simple_transaction"]
        }
    ),
    ConversationalGolden(
        scenario="Happy path - experienced user efficiently completing tasks",
        expected_outcome="User quickly completes multiple banking tasks",
        user_description="Alice, experienced user who knows what they want",
        additional_metadata={
            "user_emotion": "neutral",
            "expected_flow": ["get_balance", "get_beneficiaries", "propose_transfer", "approve_transfer"]
        }
    ),
]

# Beneficiary Management Conversations
BENEFICIARY_MANAGEMENT_SCENARIOS = [
    ConversationalGolden(
        scenario="User wants to add multiple beneficiaries and then send money to one",
        expected_outcome="User successfully adds beneficiaries and completes transfer",
        user_description="Alice, setting up beneficiaries for the first time",
        additional_metadata={
            "expected_flow": ["add_beneficiary", "add_beneficiary", "get_beneficiaries", "propose_transfer"]
        }
    ),
]

# All conversational goldens combined
ALL_CONVERSATIONAL_GOLDENS = (
    TRANSFER_WORKFLOW_SCENARIOS +
    SPENDING_ANALYSIS_SCENARIOS +
    ACCOUNT_MANAGEMENT_SCENARIOS +
    CUSTOMER_SUPPORT_SCENARIOS +
    BENEFICIARY_MANAGEMENT_SCENARIOS
)
