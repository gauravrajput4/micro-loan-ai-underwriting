import unittest

from backend.services.policy_engine import evaluate_policy


class TestPolicyEngine(unittest.TestCase):
    def test_rejects_unaffordable_amount(self):
        result = evaluate_policy(
            requested_amount=100000,
            monthly_income=1000,
            loan_recommendation={"max_loan_amount": 20000},
            emi_data={"monthly_emi": 600},
            financial_data={"savings_ratio": 0.05},
        )
        self.assertFalse(result["passed"])
        self.assertIn("AMOUNT_ABOVE_AFFORDABLE_LIMIT", result["reason_codes"])
        self.assertIn("EMI_TO_INCOME_TOO_HIGH", result["reason_codes"])


if __name__ == "__main__":
    unittest.main()

