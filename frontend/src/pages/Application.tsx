import React, { useState } from 'react';
import { motion } from 'motion/react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import axios from 'axios';

export default function Application() {

    const navigate = useNavigate();
    const location = useLocation();

    const bankData = location.state?.bankData;

    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        loan_amount: 5000,
        loan_purpose: 'Education',
        employment_status: 'student',

        monthly_income: bankData?.avg_monthly_income || 0,
        monthly_expenses: bankData?.avg_monthly_expenses || 0,

        savings:
            bankData?.avg_monthly_income && bankData?.savings_ratio
                ? bankData.avg_monthly_income * bankData.savings_ratio
                : 0,

        existing_loans: 0,

        account_balance: bankData?.avg_monthly_balance || 0
    });

    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {

        e.preventDefault();
        setIsSubmitting(true);

        try {

            const payload = {
                email: formData.email,
                full_name: formData.full_name,
                loan_amount: formData.loan_amount,
                loan_purpose: formData.loan_purpose,
                employment_status: formData.employment_status,
                monthly_income: formData.monthly_income,
                monthly_expenses: formData.monthly_expenses,
                savings: formData.savings,
                existing_loans: formData.existing_loans,
                account_balance: formData.account_balance
            };

            // Step 1 Save Application
            await axios.post(
                "http://localhost:8000/api/loan/apply-loan",
                payload
            );

            // Step 2 Predict Loan
            const res = await axios.post(
                "http://localhost:8000/api/loan/predict-loan",
                payload
            );

            navigate('/results', { state: { result: res.data } });

        } catch (error) {

            console.error("Loan prediction failed:", error);

        } finally {

            setIsSubmitting(false);

        }

    };

    return (

        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-3xl mx-auto space-y-8"
        >

            <div>
                <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
                    Loan Application
                </h1>

                <p className="text-neutral-500 mt-1">
                    Enter applicant details to run the AI underwriting model.
                </p>
            </div>

            <form
                onSubmit={handleSubmit}
                className="bg-white p-8 rounded-3xl shadow-sm border border-neutral-100 space-y-6"
            >

                {/* Personal Details */}

                <div className="space-y-4">

                    <h3 className="text-lg font-medium border-b border-neutral-100 pb-2">
                        Applicant Details
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                                Full Name
                            </label>

                            <input
                                type="text"
                                required
                                value={formData.full_name}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        full_name: e.target.value
                                    })
                                }
                                className="w-full px-4 py-3 rounded-xl border border-neutral-200"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                                Email
                            </label>

                            <input
                                type="email"
                                required
                                value={formData.email}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        email: e.target.value
                                    })
                                }
                                className="w-full px-4 py-3 rounded-xl border border-neutral-200"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                                Employment Status
                            </label>

                            <select
                                value={formData.employment_status}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        employment_status: e.target.value
                                    })
                                }
                                className="w-full px-4 py-3 rounded-xl border border-neutral-200"
                            >

                                <option value="student">Student</option>
                                <option value="unemployed">Unemployed</option>
                                <option value="employed">Employed</option>

                            </select>

                        </div>

                    </div>

                </div>

                {/* Loan Request */}

                <div className="space-y-4 pt-4">

                    <h3 className="text-lg font-medium border-b border-neutral-100 pb-2">
                        Loan Request
                    </h3>

                    <div className="grid grid-cols-2 gap-4">

                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                                Requested Amount
                            </label>

                            <input
                                type="number"
                                value={formData.loan_amount}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        loan_amount: Number(e.target.value)
                                    })
                                }
                                className="w-full px-4 py-3 rounded-xl border border-neutral-200 font-mono"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                                Purpose
                            </label>

                            <select
                                value={formData.loan_purpose}
                                onChange={e =>
                                    setFormData({
                                        ...formData,
                                        loan_purpose: e.target.value
                                    })
                                }
                                className="w-full px-4 py-3 rounded-xl border border-neutral-200"
                            >

                                <option>Education</option>
                                <option>Personal</option>
                                <option>Emergency</option>
                                <option>Medical</option>

                            </select>

                        </div>

                    </div>

                </div>

                {/* Financial Profile */}

                <div className="space-y-4 pt-4">

                    <div className="flex items-center justify-between border-b border-neutral-100 pb-2">
                        <h3 className="text-lg font-medium">
                            Financial Profile
                        </h3>

                        {bankData && (
                            <span className="text-xs font-medium bg-emerald-100 text-emerald-700 px-2 py-1 rounded-md flex items-center gap-1">
                                <Sparkles size={12}/> Auto-filled from Bank Statement
                            </span>
                        )}

                    </div>

                    <div className="grid grid-cols-2 gap-4">

                        <Metric title="Monthly Income" value={formData.monthly_income}/>
                        <Metric title="Monthly Expenses" value={formData.monthly_expenses}/>
                        <Metric title="Savings" value={formData.savings}/>
                        <Metric title="Account Balance" value={formData.account_balance}/>

                    </div>

                </div>

                <div className="pt-6">

                    <motion.button
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full bg-neutral-900 text-white py-4 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-neutral-800"
                    >

                        {isSubmitting ? "Processing..." :
                            <>Run AI Underwriting <ArrowRight size={18}/></>
                        }

                    </motion.button>

                </div>

            </form>

        </motion.div>
    );
}


function Metric({title, value}: any) {

    return (
        <div className="p-4 border border-neutral-100 rounded-xl bg-neutral-50">
            <p className="text-xs text-neutral-500 uppercase font-semibold mb-1">
                {title}
            </p>

            <p className="text-xl font-mono text-neutral-900">
                {value?.toLocaleString()}
            </p>
        </div>
    );
}