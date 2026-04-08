import re
from typing import Dict


PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
AADHAAR_PATTERN = re.compile(r"^[0-9]{12}$")
PASSPORT_PATTERN = re.compile(r"^[A-PR-WYa-pr-wy][1-9][0-9]{6}$")


class KYCValidationError(Exception):
    pass


def validate_document_number(doc_type: str, number: str) -> None:
    normalized = (number or "").strip().upper().replace(" ", "")

    if doc_type == "pan" and not PAN_PATTERN.match(normalized):
        raise KYCValidationError("Invalid PAN format")

    if doc_type == "aadhaar" and not AADHAAR_PATTERN.match(normalized):
        raise KYCValidationError("Invalid Aadhaar format")

    if doc_type == "passport" and not PASSPORT_PATTERN.match(normalized):
        raise KYCValidationError("Invalid passport format")


def mock_ocr_extract(filename: str, document_number: str) -> Dict[str, str]:
    # Placeholder OCR for MVP. Replace with OCR engine/provider in production.
    return {
        "file_name": filename,
        "extracted_document_number": (document_number or "").strip().upper(),
        "name_match_score": "0.93",
    }


def mock_liveness_check(blink_score: float, face_match_score: float) -> Dict[str, float]:
    passed = blink_score >= 0.6 and face_match_score >= 0.7
    return {
        "blink_score": blink_score,
        "face_match_score": face_match_score,
        "passed": float(1 if passed else 0),
    }

