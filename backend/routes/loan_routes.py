from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pickle
import numpy as np
import os
import pandas as pd

try:
    from database.mongodb import loan_applications_collection, loan_predictions_collection
    from services.bank_statement_analyzer import BankStatementAnalyzer
    from services.credit_score_engine import CreditScoreEngine
    from services.loan_recommendation import LoanRecommendation
    from services.emi_calculator import EMICalculator
    from services.ai_explanation import AIExplanation
except ModuleNotFoundError:
    from ..database.mongodb import loan_applications_collection, loan_predictions_collection
    from ..services.bank_statement_analyzer import BankStatementAnalyzer
    from ..services.credit_score_engine import CreditScoreEngine
    from ..services.loan_recommendation import LoanRecommendation
    from ..services.emi_calculator import EMICalculator
    from ..services.ai_explanation import AIExplanation

try:
    from services.audit_log import log_audit_event
    from services.security import AuthUser, require_roles
    from services.policy_engine import evaluate_policy
    from services.shadow_evaluator import evaluate_challenger_shadow
    from services.email_service import send_email
    from services.email_templates import build_loan_decision_email
except ModuleNotFoundError:
    from ..services.audit_log import log_audit_event
    from ..services.security import AuthUser, require_roles
    from ..services.policy_engine import evaluate_policy
    from ..services.shadow_evaluator import evaluate_challenger_shadow
    from ..services.email_service import send_email
    from ..services.email_templates import build_loan_decision_email


router = APIRouter()

try:
    import shap
except Exception:
    shap = None

# Determine the path to ML artifacts
ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml')


def _json_safe(value):
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    # bson.ObjectId is not JSON serializable by FastAPI's encoder.
    if value.__class__.__name__ == "ObjectId":
        return str(value)
    return value

def _load_model_artifacts():
    model_path = os.path.join(ML_DIR, "loan_model.pkl")
    scaler_path = os.path.join(ML_DIR, "scaler.pkl")
    config_path = os.path.join(ML_DIR, "model_config.pkl")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise HTTPException(
            status_code=503,
            detail="ML artifacts not found. Run backend/ml/train_model.py first."
        )

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    model_config = {"feature_names": None, "optimal_threshold": 0.5}
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            loaded = pickle.load(f)
            if isinstance(loaded, dict):
                model_config.update(loaded)

    return model, scaler, model_config


def _extract_shap_values(shap_values: np.ndarray, n_features: int) -> np.ndarray:
    arr = np.asarray(shap_values)
    if arr.ndim == 3:
        # Common RandomForest shape in newer SHAP versions: (samples, features, classes)
        return arr[0, :, 1]
    if arr.ndim == 2:
        return arr[0]
    if arr.ndim == 1 and arr.shape[0] == n_features:
        return arr
    raise ValueError(f"Unexpected SHAP shape: {arr.shape}")

class LoanApplication(BaseModel):
    email: str
    full_name: str
    loan_amount: float
    loan_purpose: str
    employment_status: str
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    savings: Optional[float] = None
    existing_loans: Optional[float] = None
    account_balance: Optional[float] = None


class EMIRequest(BaseModel):
    principal: float
    annual_rate: float
    tenure_months: int


def _send_loan_decision_email(
    *,
    to_email: str,
    applicant_name: str,
    decision: str,
    requested_amount: float,
    reasons: list[str],
    recommendations: list[str],
) -> None:
    payload = build_loan_decision_email(
        decision=decision,
        applicant_name=applicant_name,
        requested_amount=requested_amount,
        reasons=reasons,
        recommendations=recommendations,
    )
    send_email(
        to_email,
        payload["subject"],
        payload["text"],
        html_body=payload["html"],
    )

@router.post("/apply-loan")
async def apply_loan(
    application: LoanApplication,
    current_user: AuthUser = Depends(require_roles("applicant", "student", "unemployed", "admin")),
):
    """Submit loan application"""
    canonical_email = current_user["email"]
    app_doc = {
        **application.dict(),
        "email": canonical_email,
        "status": "submitted",
        "lifecycle": [
            {
                "status": "submitted",
                "at": datetime.utcnow(),
                "source": "applicant",
            }
        ],
        "created_at": datetime.utcnow()
    }
    
    result = loan_applications_collection.insert_one(app_doc)
    log_audit_event(
        action="loan.application.submitted",
        actor_email=current_user["email"],
        actor_role=current_user["role"],
        entity_type="loan",
        entity_id=str(result.inserted_id),
        metadata={"loan_amount": application.loan_amount, "purpose": application.loan_purpose},
    )
    print(result)
    return {
        "message": "Loan application submitted successfully",
        "application_id": str(result.inserted_id)
    }

@router.post("/predict-loan")
async def predict_loan(
    application: LoanApplication,
    current_user: AuthUser = Depends(require_roles("applicant", "student", "unemployed", "underwriter", "risk_manager", "admin")),
):
    canonical_email = current_user["email"]
    model, scaler, model_config = _load_model_artifacts()
    optimal_threshold = float(model_config.get("optimal_threshold", 0.5))

    # Analyze financial data
    analyzer = BankStatementAnalyzer()

    financial_data = analyzer.analyze_manual_entry({
        "monthly_income": application.monthly_income or 0,
        "monthly_expenses": application.monthly_expenses or 0,
        "savings": application.savings or 0,
        "existing_loans": application.existing_loans or 0,
        "account_balance": application.account_balance or 0
    })

    # Credit score
    credit_engine = CreditScoreEngine()

    credit_score = credit_engine.calculate_credit_score(financial_data)
    credit_rating = credit_engine.get_credit_rating(credit_score)

    default_feature_names = [
        "monthly_income",
        "monthly_expenses",
        "savings_ratio",
        "financial_stability_score",
        "cash_flow_stability",
        "credit_score",
        "existing_loans",
        "account_balance",
        "transaction_frequency"
    ]
    feature_names = model_config.get("feature_names") or default_feature_names

    monthly_income = float(financial_data.get("avg_monthly_income", 0) or 0)
    requested_amount = float(application.loan_amount or 0)
    amount_to_income_ratio = (requested_amount / monthly_income) if monthly_income > 0 else 0.0

    feature_map = {
        "monthly_income": monthly_income,
        "monthly_expenses": float(financial_data.get("avg_monthly_expenses", 0) or 0),
        "savings_ratio": float(financial_data.get("savings_ratio", 0) or 0),
        "financial_stability_score": float(financial_data.get("financial_stability_score", 0) or 0),
        "cash_flow_stability": float(financial_data.get("cash_flow_stability", 0) or 0),
        "credit_score": float(credit_score),
        "existing_loans": float(financial_data.get("existing_loans", 0) or 0),
        "account_balance": float(financial_data.get("avg_monthly_balance", 0) or 0),
        "transaction_frequency": float(financial_data.get("transaction_frequency", 0) or 0),
        "requested_amount": requested_amount,
        "amount_to_income_ratio": float(amount_to_income_ratio),
    }

    features_df = pd.DataFrame([feature_map]).reindex(columns=feature_names, fill_value=0.0)
    features_df = features_df.fillna(0.0)

    print("Features before scaling:", features_df)

    # Scale features
    features_scaled = scaler.transform(features_df)

    # Prediction using optimal threshold
    prediction_proba = model.predict_proba(features_scaled)[0]
    probability_approved = prediction_proba[1]
    
    # Use optimal threshold for decision (instead of default 0.5)
    prediction = 1 if probability_approved >= optimal_threshold else 0

    # SHAP explanation
    try:

        if shap is None:
            raise RuntimeError("SHAP is not installed")

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features_scaled)

        if isinstance(shap_values, list):
            shap_array = np.asarray(shap_values[1])[0]
        else:
            shap_array = _extract_shap_values(shap_values, len(feature_names))

        feature_importance = {
            feature_names[i]: float(shap_array[i])
            for i in range(len(feature_names))
        }

    except Exception as e:

        print("SHAP error:", e)

        feature_importance = {
            feature: 0 for feature in feature_names
        }

    # Generate explanation
    ai_explanation = AIExplanation()

    explanation = ai_explanation.generate_explanation(
        prediction,
        financial_data,
        feature_importance
    )

    # Loan recommendation
    loan_recommender = LoanRecommendation()

    loan_recommendation = loan_recommender.recommend_loan_amount(
        financial_data,
        credit_score
    )

    # EMI
    emi_calc = EMICalculator()

    emi_data = emi_calc.calculate_emi(
        application.loan_amount,
        12.0,
        36
    )

    # Affordability/policy guardrail on top of ML risk decision.
    policy_result = evaluate_policy(
        requested_amount=application.loan_amount,
        monthly_income=float(financial_data.get("avg_monthly_income", 0) or 0),
        loan_recommendation=loan_recommendation,
        emi_data=emi_data,
        financial_data=financial_data,
    )
    policy_pass = bool(policy_result["passed"])
    policy_reasons = list(policy_result["human_reasons"])
    policy_recommendations = list(policy_result["recommendations"])
    policy_reason_codes = list(policy_result["reason_codes"])

    if not policy_pass:
        prediction = 0
        explanation["decision"] = "rejected"
        explanation["reasons"] = list(dict.fromkeys((explanation.get("reasons") or []) + policy_reasons))
        explanation["recommendations"] = list(
            dict.fromkeys((explanation.get("recommendations") or []) + policy_recommendations)
        )
        explanation["adverse_action_codes"] = policy_reason_codes

    # Shadow challenger evaluation (no impact on production decision).
    shadow_eval = evaluate_challenger_shadow(
        email=canonical_email,
        features_df=features_df,
        champion_probability=float(prediction_proba[1]),
        champion_decision=int(prediction),
        request_id=None,
    )

    # Save prediction
    prediction_doc = {
        "email": canonical_email,
        "prediction": int(prediction),
        "probability": float(prediction_proba[1]),
        "credit_score": credit_score,
        "credit_rating": credit_rating,
        "financial_data": financial_data,
        "explanation": explanation,
        "loan_recommendation": loan_recommendation,
        "emi_data": emi_data,
        "policy_checks": {
            "passed": policy_pass,
            "reasons": policy_reasons,
            "recommendations": policy_recommendations,
            "reason_codes": policy_reason_codes,
        },
        "shadow_evaluation": shadow_eval,
        "requested_amount": application.loan_amount,
        "created_at": datetime.utcnow()
    }

    loan_predictions_collection.insert_one(prediction_doc)

    loan_applications_collection.update_one(
        {"email": canonical_email},
        {
            "$set": {
                "status": "under_review",
                "ai_decision": "approved" if prediction == 1 else "rejected",
                "ai_probability": float(prediction_proba[1]),
                "updated_at": datetime.utcnow(),
            },
            "$push": {
                "lifecycle": {
                    "status": "under_review",
                    "at": datetime.utcnow(),
                    "source": "model",
                }
            },
        },
    )

    log_audit_event(
        action="loan.model.scored",
        actor_email=canonical_email,
        actor_role="model",
        entity_type="loan",
        entity_id=canonical_email,
        metadata={
            "decision": "approved" if prediction == 1 else "rejected",
            "probability": round(float(prediction_proba[1]), 4),
            "credit_score": credit_score,
        },
    )

    print("Prediction saved:", prediction_doc)

    _send_loan_decision_email(
        to_email=canonical_email,
        applicant_name=application.full_name,
        decision="approved" if prediction == 1 else "rejected",
        requested_amount=application.loan_amount,
        reasons=explanation.get("reasons") or [],
        recommendations=explanation.get("recommendations") or [],
    )

    safe_shadow_eval = _json_safe(shadow_eval)

    return {
        "decision": "approved" if prediction == 1 else "rejected",
        "probability": round(float(prediction_proba[1]), 4),
        "credit_score": credit_score,
        "credit_rating": credit_rating,
        "financial_metrics": financial_data,
        "explanation": explanation,
        "loan_recommendation": loan_recommendation,
        "emi_details": emi_data,
        "policy_checks": prediction_doc["policy_checks"],
        "shadow_evaluation": safe_shadow_eval,
    }


@router.post("/calculate-emi")
async def calculate_emi(
    request: EMIRequest,
    current_user: AuthUser = Depends(require_roles("applicant", "student", "unemployed", "underwriter", "risk_manager", "admin", "auditor")),
):
    """Calculate EMI for given loan parameters"""
    _ = current_user
    calculator = EMICalculator()
    emi_data = calculator.calculate_emi(
        request.principal,
        request.annual_rate,
        request.tenure_months
    )
    print(emi_data)
    return emi_data
