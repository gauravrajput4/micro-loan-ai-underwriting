from typing import Dict, List


def evaluate_policy(
    *,
    requested_amount: float,
    monthly_income: float,
    loan_recommendation: Dict,
    emi_data: Dict,
    financial_data: Dict,
) -> Dict:
    """Combine scorecard/business rules with model output and return reason codes."""
    reason_codes: List[str] = []
    human_reasons: List[str] = []
    recommendations: List[str] = []

    max_allowed = float(loan_recommendation.get("max_loan_amount", 0) or 0)
    monthly_emi = float(emi_data.get("monthly_emi", 0) or 0)
    savings_ratio = float(financial_data.get("savings_ratio", 0) or 0)

    if requested_amount <= 0:
        reason_codes.append("INVALID_AMOUNT")
        human_reasons.append("Requested amount is invalid")
        recommendations.append("Enter a valid loan amount greater than zero")

    if max_allowed > 0 and requested_amount > max_allowed:
        reason_codes.append("AMOUNT_ABOVE_AFFORDABLE_LIMIT")
        human_reasons.append("Requested amount exceeds safe affordability limit")
        recommendations.append(f"Request <= {max_allowed:.2f} based on current profile")

    if monthly_income > 0 and monthly_emi > monthly_income * 0.5:
        reason_codes.append("EMI_TO_INCOME_TOO_HIGH")
        human_reasons.append("Monthly EMI would be too high for your income")
        recommendations.append("Reduce amount or increase tenure to keep EMI <= 50% of monthly income")

    if savings_ratio < 0.1:
        reason_codes.append("LOW_SAVINGS_RATIO")
        human_reasons.append("Savings ratio is below policy minimum")
        recommendations.append("Improve savings ratio before re-applying")

    return {
        "passed": len(reason_codes) == 0,
        "reason_codes": reason_codes,
        "human_reasons": human_reasons,
        "recommendations": recommendations,
    }

