from typing import Dict

class CreditScoreEngine:
    def calculate_credit_score(self, financial_data: Dict, payment_history: float = 0.8) -> int:
        """
        Generate credit score (300-850) based on financial metrics
        
        Args:
            financial_data: Financial metrics from bank statement or manual entry
            payment_history: Payment history score (0-1), default 0.8
        """
        savings_ratio = financial_data.get("savings_ratio", 0)
        financial_stability = financial_data.get("financial_stability_score", 0)
        cash_flow_stability = financial_data.get("cash_flow_stability", 0)
        avg_income = financial_data.get("avg_monthly_income", 0)
        avg_expenses = financial_data.get("avg_monthly_expenses", 0)
        
        # Income vs expenses ratio
        income_expense_ratio = (avg_income - avg_expenses) / avg_income if avg_income > 0 else 0
        
        # Weighted score calculation
        base_score = (
            payment_history * 0.35 +
            financial_stability * 0.30 +
            savings_ratio * 0.20 +
            cash_flow_stability * 0.10 +
            income_expense_ratio * 0.05
        )
        
        # Scale to 300-850 range
        credit_score = int(300 + (base_score * 550))
        credit_score = max(300, min(850, credit_score))
        
        return credit_score
    
    def get_credit_rating(self, score: int) -> str:
        """Get credit rating category"""
        if score >= 750:
            return "Excellent"
        elif score >= 700:
            return "Good"
        elif score >= 650:
            return "Fair"
        elif score >= 600:
            return "Poor"
        else:
            return "Very Poor"
