from fastapi import APIRouter, HTTPException
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


router = APIRouter()

try:
    import shap
except Exception:
    shap = None

# Determine the path to ML artifacts
ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml')

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

@router.post("/apply-loan")
async def apply_loan(application: LoanApplication):
    """Submit loan application"""
    canonical_email = application.email.strip().lower()
    app_doc = {
        **application.dict(),
        "email": canonical_email,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = loan_applications_collection.insert_one(app_doc)
    print(result)
    return {
        "message": "Loan application submitted successfully",
        "application_id": str(result.inserted_id)
    }

@router.post("/predict-loan")
async def predict_loan(application: LoanApplication):
    canonical_email = application.email.strip().lower()
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

    # Prepare feature values
    feature_values = [[
        financial_data["avg_monthly_income"],
        financial_data["avg_monthly_expenses"],
        financial_data["savings_ratio"],
        financial_data["financial_stability_score"],
        financial_data["cash_flow_stability"],
        credit_score,
        financial_data.get("existing_loans", 0),
        financial_data["avg_monthly_balance"],
        financial_data["transaction_frequency"]
    ]]

    features_df = pd.DataFrame(feature_values, columns=default_feature_names)
    features_df = features_df.reindex(columns=feature_names)

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
        "requested_amount": application.loan_amount,
        "created_at": datetime.utcnow()
    }

    loan_predictions_collection.insert_one(prediction_doc)

    print("Prediction saved:", prediction_doc)

    return {
        "decision": "approved" if prediction == 1 else "rejected",
        "probability": round(float(prediction_proba[1]), 4),
        "credit_score": credit_score,
        "credit_rating": credit_rating,
        "financial_metrics": financial_data,
        "explanation": explanation,
        "loan_recommendation": loan_recommendation,
        "emi_details": emi_data
    }


@router.post("/calculate-emi")
async def calculate_emi(request: EMIRequest):
    """Calculate EMI for given loan parameters"""
    calculator = EMICalculator()
    emi_data = calculator.calculate_emi(
        request.principal,
        request.annual_rate,
        request.tenure_months
    )
    print(emi_data)
    return emi_data
