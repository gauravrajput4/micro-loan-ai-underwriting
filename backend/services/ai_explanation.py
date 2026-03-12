from typing import Dict, List

class AIExplanation:
    def generate_explanation(self, prediction: int, financial_data: Dict, feature_importance: Dict) -> Dict:
        """
        Generate human-readable explanation for loan decision
        
        Args:
            prediction: 1 for approved, 0 for rejected
            financial_data: Financial metrics
            feature_importance: SHAP feature importance values
        """
        decision = "approved" if prediction == 1 else "rejected"
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = sorted_features[:5]
        
        reasons = []
        recommendations = []
        
        # Analyze key factors
        savings_ratio = financial_data.get("savings_ratio", 0)
        financial_stability = financial_data.get("financial_stability_score", 0)
        cash_flow_stability = financial_data.get("cash_flow_stability", 0)
        avg_income = financial_data.get("avg_monthly_income", 0)
        
        if prediction == 0:  # Rejected
            if savings_ratio < 0.2:
                reasons.append("Low savings ratio - expenses are too high relative to income")
                recommendations.append("Reduce monthly expenses by at least 20%")
            
            if financial_stability < 0.5:
                reasons.append("Poor financial stability score")
                recommendations.append("Build emergency savings equal to 3-6 months of expenses")
            
            if cash_flow_stability < 0.4:
                reasons.append("Unstable cash flow patterns")
                recommendations.append("Maintain consistent income and avoid irregular large expenses")
            
            if avg_income < 20000:
                reasons.append("Insufficient monthly income")
                recommendations.append("Increase income sources or wait until income improves")
        
        else:  # Approved
            if savings_ratio > 0.3:
                reasons.append("Strong savings ratio demonstrates financial discipline")
            
            if financial_stability > 0.6:
                reasons.append("Good financial stability score")
            
            if cash_flow_stability > 0.6:
                reasons.append("Stable and consistent cash flow")
            
            if avg_income > 30000:
                reasons.append("Sufficient monthly income to support loan repayment")
        
        return {
            "decision": decision,
            "reasons": reasons if reasons else ["Standard risk assessment criteria met"],
            "recommendations": recommendations if recommendations else ["Continue maintaining good financial habits"],
            "top_risk_features": [{"feature": f[0], "importance": round(f[1], 4)} for f in top_features],
            "confidence": self._calculate_confidence(financial_data)
        }
    
    def _calculate_confidence(self, financial_data: Dict) -> float:
        """Calculate prediction confidence score"""
        stability = financial_data.get("financial_stability_score", 0)
        savings = financial_data.get("savings_ratio", 0)
        cash_flow = financial_data.get("cash_flow_stability", 0)
        
        confidence = (stability + savings + cash_flow) / 3
        return round(confidence, 2)
