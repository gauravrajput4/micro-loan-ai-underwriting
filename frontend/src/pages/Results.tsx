import { motion } from "motion/react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";

import {
    CheckCircle2,
    XCircle,
    AlertTriangle,
    ArrowLeft,
    Calculator,
} from "lucide-react";

export default function Results() {

    const location = useLocation();
    const navigate = useNavigate();

    const result = location.state?.result;

    if (!result) {
        return (
            <div className="text-center py-20">
                <p>No results found. Please submit an application first.</p>
                <button
                    onClick={() => navigate("/apply")}
                    className="mt-4 text-emerald-600 underline"
                >
                    Go back
                </button>
            </div>
        );
    }

    const isApproved = result.decision === "approved";

    const riskScore = 1 - result.probability;

    const explanationText = result.explanation?.reasons?.join(", ") || "AI decision explanation";

    const shapValues =
        result.explanation?.top_risk_features?.map((f: any) => ({
            feature: f.feature,
            impact: f.importance,
        })) || [];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto space-y-8"
        >

            {/* Header */}

            <div className="flex items-center justify-between">

                <div>

                    <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
                        AI Decision Report
                    </h1>

                    <p className="text-neutral-500 mt-1">
                        Credit Rating:
                        <span className="font-medium text-neutral-900 ml-1">
              {result.credit_rating}
            </span>
                    </p>

                </div>

                <button
                    onClick={() => navigate("/apply")}
                    className="flex items-center gap-2 text-sm font-medium text-neutral-500 hover:text-neutral-900 transition-colors"
                >
                    <ArrowLeft size={16} /> New Application
                </button>

            </div>

            {/* Decision Banner */}

            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className={`p-8 rounded-3xl flex items-start gap-6 ${
                    isApproved ? "bg-emerald-500 text-white" : "bg-red-500 text-white"
                }`}
            >

                <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
                    {isApproved ? <CheckCircle2 size={40} /> : <XCircle size={40} />}
                </div>

                <div>

                    <h2 className="text-3xl font-semibold mb-2">
                        Loan {result.decision.toUpperCase()}
                    </h2>

                    <p className="text-white/90 text-lg max-w-2xl leading-relaxed">
                        {explanationText}
                    </p>

                </div>

            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Metrics */}

                <div className="space-y-6">

                    <MetricCard
                        title="AI Risk Score"
                        value={riskScore.toFixed(2)}
                        max="1.0"
                    />

                    <MetricCard
                        title="Generated Credit Score"
                        value={result.credit_score}
                        max="850"
                    />

                    {isApproved && (
                        <div className="bg-neutral-900 p-6 rounded-2xl text-white">

                            <h3 className="text-sm font-medium text-neutral-400 mb-1">
                                Recommended Max Amount
                            </h3>

                            <p className="text-3xl font-mono font-semibold">
                                ${result.loan_recommendation.recommended_loan_amount.toLocaleString()}
                            </p>

                            <button
                                onClick={() =>
                                    navigate("/calculator", {
                                        state: {
                                            amount:
                                            result.loan_recommendation.recommended_loan_amount,
                                        },
                                    })
                                }
                                className="mt-6 w-full bg-white text-neutral-900 py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 hover:bg-neutral-100 transition-colors"
                            >
                                <Calculator size={16} /> Calculate EMI
                            </button>

                        </div>
                    )}

                </div>

                {/* SHAP Chart */}

                <div className="md:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">

                    <div className="flex items-center gap-2 mb-6">
                        <AlertTriangle size={20} className="text-amber-500" />
                        <h3 className="text-lg font-semibold">AI Feature Importance</h3>
                    </div>

                    <p className="text-sm text-neutral-500 mb-6">
                        Features that influenced the loan decision.
                    </p>

                    <div className="h-64">

                        <ResponsiveContainer width="100%" height="100%">

                            <BarChart
                                data={shapValues}
                                layout="vertical"
                                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                            >

                                <CartesianGrid strokeDasharray="3 3" />

                                <XAxis type="number" />

                                <YAxis
                                    dataKey="feature"
                                    type="category"
                                    width={120}
                                />

                                <Tooltip />

                                <Bar dataKey="impact">

                                    {shapValues.map((entry: any, index: number) => (
                                        <Cell
                                            key={index}
                                            fill={entry.impact > 0 ? "#ef4444" : "#10b981"}
                                        />
                                    ))}

                                </Bar>

                            </BarChart>

                        </ResponsiveContainer>

                    </div>

                </div>

            </div>

        </motion.div>
    );
}


/* Metric Component */

function MetricCard({ title, value, max }: any) {

    const percentage = (Number(value) / Number(max)) * 100;

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">

            <h3 className="text-sm font-medium text-neutral-500 mb-1">
                {title}
            </h3>

            <div className="flex items-end gap-2">

        <span className="text-4xl font-mono font-semibold text-neutral-900">
          {value}
        </span>

                <span className="text-sm text-neutral-400 mb-1">
          / {max}
        </span>

            </div>

            <div className="w-full bg-neutral-100 h-2 rounded-full mt-4 overflow-hidden">

                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    className="h-full bg-emerald-500"
                />

            </div>

        </div>
    );
}