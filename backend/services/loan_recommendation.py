from typing import Dict

class LoanRecommendation:
    def recommend_loan_amount(self, financial_data: Dict, credit_score: int) -> Dict:
        """
        Recommend safe loan amount based on financial metrics
        
        Rule: Maximum Loan Amount = 30% of Annual Income
        Adjusted by credit score and savings ratio
        """
        monthly_income = financial_data.get("avg_monthly_income", 0)
        annual_income = monthly_income * 12
        savings_ratio = financial_data.get("savings_ratio", 0)
        existing_loans = financial_data.get("existing_loans", 0)
        
        # Base loan amount (30% of annual income)
        base_loan_amount = annual_income * 0.30
        
        # Credit score multiplier
        if credit_score >= 750:
            credit_multiplier = 1.2
        elif credit_score >= 700:
            credit_multiplier = 1.0
        elif credit_score >= 650:
            credit_multiplier = 0.8
        elif credit_score >= 600:
            credit_multiplier = 0.6
        else:
            credit_multiplier = 0.4
        
        # Savings ratio adjustment
        savings_multiplier = 1 + (savings_ratio * 0.5)
        
        # Calculate recommended amount
        recommended_amount = base_loan_amount * credit_multiplier * savings_multiplier
        
        # Adjust for existing loans
        debt_to_income = existing_loans / annual_income if annual_income > 0 else 0
        if debt_to_income > 0.4:
            recommended_amount *= 0.5
        
        return {
            "recommended_loan_amount": round(recommended_amount, 2),
            "min_loan_amount": round(recommended_amount * 0.3, 2),
            "max_loan_amount": round(recommended_amount * 1.5, 2),
            "debt_to_income_ratio": round(debt_to_income, 2)
        }
