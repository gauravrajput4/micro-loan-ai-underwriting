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

type RiskFeature = {
    feature: string;
    importance: number;
};

type PredictionResult = {
    decision?: string;
    prediction?: number;
    probability?: number;
    credit_score?: number;
    credit_rating?: string;
    requested_amount?: number;
    explanation?: {
        decision?: string;
        reasons?: string[];
        recommendations?: string[];
        confidence?: number;
        top_risk_features?: RiskFeature[];
    };
    financial_data?: Record<string, number>;
    financial_metrics?: Record<string, number>;
    loan_recommendation?: Record<string, number>;
    emi_data?: Record<string, number>;
    emi_details?: Record<string, number>;
};

function toNumber(value: unknown, fallback = 0): number {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
}

function formatCurrency(value: unknown): string {
    return `₹${toNumber(value).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;
}

export default function Results() {

    const location = useLocation();
    const navigate = useNavigate();

    const result = location.state?.result as PredictionResult | undefined;

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

    const normalizedDecision = (
        result.decision ||
        result.explanation?.decision ||
        (result.prediction === 1 ? "approved" : "rejected")
    ).toLowerCase();

    const isApproved = normalizedDecision === "approved";

    const probability = toNumber(result.probability);
    const riskScore = Math.min(Math.max(1 - probability, 0), 1);

    const reasons = Array.isArray(result.explanation?.reasons)
        ? result.explanation?.reasons
        : [];
    const recommendations = Array.isArray(result.explanation?.recommendations)
        ? result.explanation?.recommendations
        : [];

    const explanationText = reasons.join(", ") || "AI decision explanation";

    const financialData = result.financial_data || result.financial_metrics || {};
    const loanRecommendation = result.loan_recommendation || {};
    const emiData = result.emi_data || result.emi_details || {};
    const requestedAmount =
        result.requested_amount ?? (emiData.principal as number | undefined);

    const rawRiskFeatures = Array.isArray(result.explanation?.top_risk_features)
        ? result.explanation?.top_risk_features
        : [];

    const shapValues = rawRiskFeatures.map((feature, index) => ({
        feature: feature.feature || `Feature ${index + 1}`,
        impact: toNumber(feature.importance),
    }));

    const hasShapData = shapValues.length > 0 && shapValues.some((item) => item.impact !== 0);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto space-y-6 sm:space-y-8"
        >

            {/* Header */}

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">

                <div>

                    <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-neutral-900">
                        AI Decision Report
                    </h1>

                    <p className="text-neutral-500 mt-1">
                        Credit Rating:
                        <span className="font-medium text-neutral-900 ml-1">
                            {result.credit_rating || "N/A"}
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
                className={`p-5 sm:p-8 rounded-3xl flex flex-col sm:flex-row items-start gap-4 sm:gap-6 ${
                    isApproved ? "bg-emerald-500 text-white" : "bg-red-500 text-white"
                }`}
            >

                <div className="bg-white/20 p-4 rounded-2xl backdrop-blur-sm">
                    {isApproved ? <CheckCircle2 size={40} /> : <XCircle size={40} />}
                </div>

                <div>

                    <h2 className="text-2xl sm:text-3xl font-semibold mb-2">
                        Loan {normalizedDecision.toUpperCase()}
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
                        value={toNumber(result.credit_score)}
                        max="850"
                    />

                    {Object.keys(loanRecommendation).length > 0 && (
                        <div className="bg-neutral-900 p-6 rounded-2xl text-white">

                            <h3 className="text-sm font-medium text-neutral-400 mb-1">
                                Recommended Max Amount
                            </h3>

                            <p className="text-3xl font-mono font-semibold">
                                {formatCurrency(loanRecommendation.recommended_loan_amount)}
                            </p>

                            <button
                                onClick={() =>
                                    navigate("/calculator", {
                                        state: {
                                            amount:
                                                toNumber(loanRecommendation.recommended_loan_amount),
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

                <div className="md:col-span-2 bg-white p-4 sm:p-6 rounded-2xl shadow-sm border border-neutral-100">

                    <div className="flex items-center gap-2 mb-6">
                        <AlertTriangle size={20} className="text-amber-500" />
                        <h3 className="text-lg font-semibold">AI Feature Importance</h3>
                    </div>

                    <p className="text-sm text-neutral-500 mb-6">
                        Features that influenced the loan decision.
                    </p>

                    {!hasShapData ? (
                        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                            Feature importance is not available for this prediction (the backend reported a SHAP processing issue).
                        </div>
                    ) : (
                        <div className="h-64">

                            <ResponsiveContainer width="100%" height="100%">

                                <BarChart
                                    data={shapValues}
                                    layout="vertical"
                                    margin={{ top: 5, right: 10, left: 20, bottom: 5 }}
                                >

                                    <CartesianGrid strokeDasharray="3 3" />

                                    <XAxis type="number" />

                                    <YAxis
                                        dataKey="feature"
                                        type="category"
                                        width={90}
                                    />

                                    <Tooltip />

                                    <Bar dataKey="impact">

                                        {shapValues.map((entry, index) => (
                                            <Cell
                                                key={index}
                                                fill={entry.impact > 0 ? "#ef4444" : "#10b981"}
                                            />
                                        ))}

                                    </Bar>

                                </BarChart>

                            </ResponsiveContainer>

                        </div>
                    )}

                </div>

            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">
                    <h3 className="text-lg font-semibold mb-4">Decision Explanation</h3>

                    <p className="text-sm text-neutral-500 mb-2">Reasons</p>
                    <ul className="space-y-2 text-sm text-neutral-700 mb-5">
                        {(reasons.length > 0 ? reasons : ["No explanation reasons returned."]).map((item) => (
                            <li key={item}>- {item}</li>
                        ))}
                    </ul>

                    <p className="text-sm text-neutral-500 mb-2">Recommendations</p>
                    <ul className="space-y-2 text-sm text-neutral-700">
                        {(recommendations.length > 0
                            ? recommendations
                            : ["No recommendations returned."]).map((item) => (
                            <li key={item}>- {item}</li>
                        ))}
                    </ul>
                </div>

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">
                    <h3 className="text-lg font-semibold mb-4">Financial Snapshot</h3>

                    <DataRow
                        label="Monthly Income"
                        value={formatCurrency(financialData.avg_monthly_income)}
                    />
                    <DataRow
                        label="Monthly Expenses"
                        value={formatCurrency(financialData.avg_monthly_expenses)}
                    />
                    <DataRow
                        label="Savings Ratio"
                        value={toNumber(financialData.savings_ratio).toFixed(2)}
                    />
                    <DataRow
                        label="Financial Stability"
                        value={toNumber(financialData.financial_stability_score).toFixed(2)}
                    />
                    <DataRow
                        label="Cash Flow Stability"
                        value={toNumber(financialData.cash_flow_stability).toFixed(2)}
                    />
                    <DataRow
                        label="Avg Balance"
                        value={formatCurrency(financialData.avg_monthly_balance)}
                    />
                </div>

            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">
                    <h3 className="text-lg font-semibold mb-4">Loan Recommendation</h3>
                    <DataRow
                        label="Recommended Amount"
                        value={formatCurrency(loanRecommendation.recommended_loan_amount)}
                    />
                    <DataRow
                        label="Minimum Amount"
                        value={formatCurrency(loanRecommendation.min_loan_amount)}
                    />
                    <DataRow
                        label="Maximum Amount"
                        value={formatCurrency(loanRecommendation.max_loan_amount)}
                    />
                    <DataRow
                        label="Debt-to-Income Ratio"
                        value={toNumber(loanRecommendation.debt_to_income_ratio).toFixed(2)}
                    />
                </div>

                {isApproved && Object.keys(emiData).length > 0 && (
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">
                        <h3 className="text-lg font-semibold mb-4">EMI Breakdown</h3>
                        <DataRow
                            label="Requested Amount"
                            value={formatCurrency(requestedAmount)}
                        />
                        <DataRow
                            label="Monthly EMI"
                            value={formatCurrency(emiData.monthly_emi)}
                        />
                        <DataRow
                            label="Total Interest"
                            value={formatCurrency(emiData.total_interest)}
                        />
                        <DataRow
                            label="Total Payment"
                            value={formatCurrency(emiData.total_payment)}
                        />
                        <DataRow
                            label="Tenure (Months)"
                            value={`${toNumber(emiData.tenure_months, 0)}`}
                        />
                    </div>
                )}

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

function DataRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between py-1.5 text-sm">
            <span className="text-neutral-500">{label}</span>
            <span className="font-medium text-neutral-900">{value}</span>
        </div>
    );
}
