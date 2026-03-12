import { useState } from "react";
import { motion } from "motion/react";
import { Calculator, DollarSign, Percent, Calendar } from "lucide-react";
import { loanAPI } from "@/src/services/api";

export default function EmiCalculator() {

    const [formData, setFormData] = useState({
        loanAmount: 10000,
        interestRate: 5.5,
        durationMonths: 36
    });

    const [result, setResult] = useState<{
        monthlyEMI: number;
        totalInterest: number;
        totalPayment: number;
    } | null>(null);


    const calculate = async () => {
        try {

            const response = await loanAPI.calculateEMI({
                principal: formData.loanAmount,
                annual_rate: formData.interestRate,
                tenure_months: formData.durationMonths
            });

            const formatted = {
                monthlyEMI: response.monthly_emi,
                totalInterest: response.total_interest,
                totalPayment: response.total_payment
            };

            setResult(formatted);

            console.log("EMI Result:", response);

        } catch (error) {
            console.error("Calculation failed:", error);
        }
    };


    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-4xl mx-auto space-y-8"
        >

            <div>
                <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
                    EMI Calculator
                </h1>
                <p className="text-neutral-500 mt-1">
                    Estimate monthly payments and total interest.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                {/* INPUT SECTION */}
                <div className="bg-white p-8 rounded-3xl shadow-sm border border-neutral-100 space-y-6">

                    {/* Loan Amount */}
                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-1.5 flex items-center gap-2">
                            <DollarSign size={16} className="text-emerald-500" />
                            Loan Amount
                        </label>

                        <input
                            type="number"
                            value={formData.loanAmount}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    loanAmount: Number(e.target.value)
                                })
                            }
                            className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-mono"
                        />

                        <input
                            type="range"
                            min="1000"
                            max="50000"
                            step="1000"
                            value={formData.loanAmount}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    loanAmount: Number(e.target.value)
                                })
                            }
                            className="w-full mt-4 accent-emerald-500"
                        />
                    </div>

                    {/* Interest Rate */}
                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-1.5 flex items-center gap-2">
                            <Percent size={16} className="text-emerald-500" />
                            Interest Rate (Annual)
                        </label>

                        <input
                            type="number"
                            step="0.1"
                            value={formData.interestRate}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    interestRate: Number(e.target.value)
                                })
                            }
                            className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-mono"
                        />

                        <input
                            type="range"
                            min="1"
                            max="25"
                            step="0.1"
                            value={formData.interestRate}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    interestRate: Number(e.target.value)
                                })
                            }
                            className="w-full mt-4 accent-emerald-500"
                        />
                    </div>

                    {/* Duration */}
                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-1.5 flex items-center gap-2">
                            <Calendar size={16} className="text-emerald-500" />
                            Duration (Months)
                        </label>

                        <input
                            type="number"
                            value={formData.durationMonths}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    durationMonths: Number(e.target.value)
                                })
                            }
                            className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-mono"
                        />

                        <input
                            type="range"
                            min="6"
                            max="120"
                            step="6"
                            value={formData.durationMonths}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    durationMonths: Number(e.target.value)
                                })
                            }
                            className="w-full mt-4 accent-emerald-500"
                        />
                    </div>

                    {/* Calculate Button */}
                    <button
                        onClick={calculate}
                        className="w-full bg-neutral-900 text-white py-3.5 rounded-xl font-medium hover:bg-neutral-800 transition-colors flex items-center justify-center gap-2"
                    >
                        Calculate
                        <Calculator size={18} />
                    </button>

                </div>

                {/* RESULT SECTION */}
                <div className="bg-neutral-900 p-8 rounded-3xl shadow-sm text-white flex flex-col justify-center relative overflow-hidden">

                    <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>

                    <div className="relative z-10 space-y-8">

                        <div>
                            <p className="text-neutral-400 text-sm font-medium mb-1">
                                Monthly EMI
                            </p>

                            <p className="text-5xl font-mono font-semibold text-emerald-400">
                                ₹{result?.monthlyEMI?.toLocaleString() || "0.00"}
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-6 pt-6 border-t border-white/10">

                            <div>
                                <p className="text-neutral-400 text-sm font-medium mb-1">
                                    Total Interest
                                </p>

                                <p className="text-2xl font-mono font-medium">
                                    ₹{result?.totalInterest?.toLocaleString() || "0.00"}
                                </p>
                            </div>

                            <div>
                                <p className="text-neutral-400 text-sm font-medium mb-1">
                                    Total Payment
                                </p>

                                <p className="text-2xl font-mono font-medium">
                                    ₹{result?.totalPayment?.toLocaleString() || "0.00"}
                                </p>
                            </div>

                        </div>

                    </div>

                </div>

            </div>
        </motion.div>
    );
}