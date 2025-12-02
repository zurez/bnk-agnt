
import unittest
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bankbot.nodes.grounding_validator import GroundingValidator

class TestGroundingValidator(unittest.TestCase):
    def setUp(self):
        self.validator = GroundingValidator()

    def test_grounded_balance(self):
        # Simulate tool result
        self.validator.register_tool_result("get_balance", '{"accounts": [{"name": "Savings", "balance": 5000.00}]}')
        
        # Test grounded response
        response = "Your Savings account balance is 5,000.00 AED."
        validation = self.validator.validate_response(response)
        self.assertTrue(validation['is_grounded'])
        self.assertEqual(len(validation['issues']), 0)

    def test_ungrounded_balance(self):
        # Simulate tool result
        self.validator.register_tool_result("get_balance", '{"accounts": [{"name": "Savings", "balance": 5000.00}]}')
        
        # Test ungrounded response (hallucinated amount)
        response = "Your Savings account balance is 10,000.00 AED."
        validation = self.validator.validate_response(response)
        self.assertFalse(validation['is_grounded'])
        self.assertEqual(len(validation['issues']), 1)
        self.assertEqual(validation['issues'][0]['type'], 'ungrounded_financial_claim')

    def test_floating_point_tolerance(self):
        # Simulate tool result
        self.validator.register_tool_result("get_balance", '{"balance": 100.00}')
        
        # Test close enough value
        response = "You have 100 AED."
        validation = self.validator.validate_response(response)
        self.assertTrue(validation['is_grounded'])

    def test_transaction_amount(self):
        # Simulate tool result
        self.validator.register_tool_result("get_transactions", '[{"amount": 50.25, "merchant": "Uber"}]')
        
        # Test grounded transaction
        response = "You spent 50.25 on Uber."
        validation = self.validator.validate_response(response)
        self.assertTrue(validation['is_grounded'])
        
        # Test ungrounded transaction
        response = "You spent 75.00 on Uber."
        validation = self.validator.validate_response(response)
        self.assertFalse(validation['is_grounded'])

    def test_multiple_values(self):
        self.validator.register_tool_result("get_balance", '{"balance": 1000}')
        self.validator.register_tool_result("get_transactions", '[{"amount": 50}]')
        
        # Mixed grounded and ungrounded
        response = "Balance is 1000 and you spent 50. You also have 999 hidden coins."
        validation = self.validator.validate_response(response)
        self.assertFalse(validation['is_grounded'])
        # Should find the 999 as ungrounded
        found_ungrounded = any(i['value'] == '999' or '999' in i['value'] for i in validation['issues'])
        self.assertTrue(found_ungrounded)

if __name__ == '__main__':
    unittest.main()
