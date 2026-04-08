import unittest

try:
    from ..services.kyc_engine import KYCValidationError, validate_document_number
except (ImportError, ModuleNotFoundError):
    from backend.services.kyc_engine import KYCValidationError, validate_document_number


class TestKycEngine(unittest.TestCase):
    def test_valid_pan(self):
        validate_document_number("pan", "ABCDE1234F")

    def test_invalid_pan(self):
        with self.assertRaises(KYCValidationError):
            validate_document_number("pan", "abc123")

    def test_valid_aadhaar(self):
        validate_document_number("aadhaar", "123456789012")

    def test_invalid_aadhaar(self):
        with self.assertRaises(KYCValidationError):
            validate_document_number("aadhaar", "12345")


if __name__ == "__main__":
    unittest.main()

