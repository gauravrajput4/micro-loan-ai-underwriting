import unittest

from backend.services.email_templates import (
    build_loan_decision_email,
    build_otp_email,
    build_password_reset_email,
)


class TestEmailTemplates(unittest.TestCase):
    def test_approved_template(self):
        payload = build_loan_decision_email(
            decision="approved",
            applicant_name="Gaurav",
            requested_amount=5000,
            reasons=["Strong savings ratio"],
            recommendations=["Complete KYC"],
        )
        self.assertIn("EduLend", payload["html"])
        self.assertIn("Approved", payload["html"])
        self.assertIn("Loan Approval", payload["subject"])

    def test_rejected_template_has_reasons(self):
        payload = build_loan_decision_email(
            decision="rejected",
            applicant_name="Gaurav",
            requested_amount=5000,
            reasons=["EMI too high"],
            recommendations=["Reduce amount"],
        )
        self.assertIn("Rejected", payload["html"])
        self.assertIn("EMI too high", payload["html"])

    def test_otp_template_contains_code_and_branding(self):
        payload = build_otp_email(
            applicant_name="Gaurav",
            otp_code="123456",
            purpose="mfa_login",
            expiry_minutes=5,
        )
        self.assertIn("123456", payload["html"])
        self.assertIn("EduLend", payload["html"])
        self.assertIn("Verification Code", payload["subject"])

    def test_password_reset_template_contains_token(self):
        payload = build_password_reset_email(
            applicant_name="Gaurav",
            reset_token="token-abc-123",
            expiry_minutes=15,
        )
        self.assertIn("token-abc-123", payload["html"])
        self.assertIn("Password Reset", payload["subject"])


if __name__ == "__main__":
    unittest.main()

