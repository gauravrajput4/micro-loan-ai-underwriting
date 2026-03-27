export function predictLoanRisk(data: any) {
  // Simulate a Machine Learning Model (e.g., Random Forest)
  // In a real Python backend, this would load a .pkl model and run inference.
  
  const { creditScore, loanAmount, averageMonthlyIncome, savingsRatio } = data;
  
  let riskScore = 0.5; // 0 = Low Risk, 1 = High Risk
  
  // Feature impact simulation
  if (creditScore > 700) riskScore -= 0.3;
  if (creditScore < 600) riskScore += 0.3;
  
  const dti = loanAmount / (averageMonthlyIncome * 12 || 1);
  if (dti > 0.3) riskScore += 0.2;
  if (dti < 0.1) riskScore -= 0.1;
  
  if (savingsRatio < 0.1) riskScore += 0.15;
  
  riskScore = Math.min(Math.max(riskScore, 0), 1);
  
  const decision = riskScore < 0.5 ? 'Approved' : 'Rejected';
  
  // Simulate SHAP Explainability
  const shapValues = [
    { feature: 'Credit Score', impact: creditScore > 650 ? -0.25 : 0.3 },
    { feature: 'Debt-to-Income', impact: dti > 0.3 ? 0.2 : -0.1 },
    { feature: 'Savings Ratio', impact: savingsRatio < 0.1 ? 0.15 : -0.05 },
    { feature: 'Late Payments', impact: data.latePaymentHistory === 'High' ? 0.2 : -0.1 }
  ].sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

  // Generate Human-Readable Explanation
  let explanation = '';
  if (decision === 'Rejected') {
    const topRisks = shapValues.filter(v => v.impact > 0).slice(0, 2).map(v => v.feature);
    explanation = `Loan rejected primarily due to high risk associated with: ${topRisks.join(' and ')}.`;
  } else {
    const topPositives = shapValues.filter(v => v.impact < 0).slice(0, 2).map(v => v.feature);
    explanation = `Loan approved. Strong positive indicators: ${topPositives.join(' and ')}.`;
  }

  // Recommend Loan Amount
  const recommendedAmount = Math.round((averageMonthlyIncome * 12) * 0.3);

  return {
    riskScore: Number(riskScore.toFixed(2)),
    decision,
    shapValues,
    explanation,
    recommendedAmount
  };
}
