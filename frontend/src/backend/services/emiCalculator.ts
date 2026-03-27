export function calculateEMI(principal: number, annualRate: number, months: number) {
  const monthlyRate = annualRate / 12 / 100;
  const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
  
  const totalPayment = emi * months;
  const totalInterest = totalPayment - principal;

  return {
    monthlyEMI: Math.round(emi * 100) / 100,
    totalInterest: Math.round(totalInterest * 100) / 100,
    totalPayment: Math.round(totalPayment * 100) / 100
  };
}
