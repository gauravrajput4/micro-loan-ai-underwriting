export function generateCreditScore(data: any) {
  // Simulate credit score generation based on input data
  // Score range: 300 - 850
  
  let baseScore = 600;
  
  if (data.financialStabilityScore) {
    baseScore += (data.financialStabilityScore - 0.5) * 200;
  }
  
  if (data.savingsRatio) {
    baseScore += data.savingsRatio * 100;
  }
  
  if (data.latePaymentHistory === 'High') {
    baseScore -= 100;
  } else if (data.latePaymentHistory === 'Low') {
    baseScore += 50;
  }

  return Math.min(Math.max(Math.round(baseScore), 300), 850);
}
