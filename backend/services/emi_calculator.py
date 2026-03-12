import math
from typing import Dict

class EMICalculator:
    def calculate_emi(self, principal: float, annual_rate: float, tenure_months: int) -> Dict:
        """
        Calculate EMI using formula:
        EMI = (P × r × (1+r)^n) / ((1+r)^n − 1)
        
        Args:
            principal: Loan amount
            annual_rate: Annual interest rate (percentage)
            tenure_months: Loan duration in months
        """
        if principal <= 0 or annual_rate <= 0 or tenure_months <= 0:
            return {
                "monthly_emi": 0,
                "total_interest": 0,
                "total_payment": 0,
                "principal": principal,
                "interest_rate": annual_rate,
                "tenure_months": tenure_months
            }
        
        # Convert annual rate to monthly rate
        monthly_rate = (annual_rate / 100) / 12
        
        # Calculate EMI
        emi_numerator = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
        emi_denominator = math.pow(1 + monthly_rate, tenure_months) - 1
        
        monthly_emi = emi_numerator / emi_denominator if emi_denominator != 0 else 0
        
        total_payment = monthly_emi * tenure_months
        total_interest = total_payment - principal
        
        return {
            "monthly_emi": round(monthly_emi, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
            "principal": principal,
            "interest_rate": annual_rate,
            "tenure_months": tenure_months
        }
    
    def generate_amortization_schedule(self, principal: float, annual_rate: float, tenure_months: int) -> list:
        """Generate month-by-month amortization schedule"""
        emi_data = self.calculate_emi(principal, annual_rate, tenure_months)
        monthly_emi = emi_data["monthly_emi"]
        monthly_rate = (annual_rate / 100) / 12
        
        schedule = []
        balance = principal
        
        for month in range(1, tenure_months + 1):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_emi - interest_payment
            balance -= principal_payment
            
            schedule.append({
                "month": month,
                "emi": round(monthly_emi, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "balance": round(max(0, balance), 2)
            })
        
        return schedule
