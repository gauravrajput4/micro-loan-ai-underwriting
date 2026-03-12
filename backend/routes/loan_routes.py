from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pickle
import numpy as np
import shap

from database.mongodb import loan_applications_collection, loan_predictions_collection
from services.bank_statement_analyzer import BankStatementAnalyzer
from services.credit_score_engine import CreditScoreEngine
from services.loan_recommendation import LoanRecommendation
from services.emi_calculator import EMICalculator
from services.ai_explanation import AIExplanation


router = APIRouter()

# Load ML model and scaler
with open('backend/ml/loan_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('backend/ml/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

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
    app_doc = {
        **application.dict(),
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

    # Feature names
    feature_names = [
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

    # Convert to DataFrame (fix scaler warning)
    import pandas as pd

    features_df = pd.DataFrame(feature_values, columns=feature_names)

    print("Features before scaling:", features_df)

    # Scale features
    features_scaled = scaler.transform(features_df)

    # Prediction
    prediction = model.predict(features_scaled)[0]
    prediction_proba = model.predict_proba(features_scaled)[0]

    # SHAP explanation
    try:

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features_scaled)

        # Handle SHAP output shape safely
        if isinstance(shap_values, list):
            shap_array = shap_values[1][0]   # positive class
        else:
            shap_array = shap_values[0]

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
        "email": application.email,
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
