import React, { useState } from "react";
import { motion } from "motion/react";
import { useNavigate } from "react-router-dom";
import { UploadCloud, FileText, CheckCircle2 } from "lucide-react";
import { uploadAPI } from "@/src/services/api";

export default function BankUpload() {

    const navigate = useNavigate();

    const [file, setFile] = useState<File | null>(null);
    const [analysis, setAnalysis] = useState<any>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const userEmail = "gaurav@gmail.com"; // replace with logged-in user email

    // File select
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {

        if (e.target.files && e.target.files[0]) {

            console.log("Selected file:", e.target.files[0]);

            setFile(e.target.files[0]);
            setError(null);

        }

    };

    // Upload file
    const handleUpload = async () => {

        if (!file) {
            setError("Please select a file first");
            return;
        }

        try {

            setIsUploading(true);

            console.log("Uploading file to backend...");

            const res = await uploadAPI.uploadBankStatement(userEmail, file);

            console.log("API RESPONSE:", res);

            setAnalysis(res);

        } catch (err) {

            console.error("Upload failed:", err);

            setError("Upload failed. Please check backend.");

        } finally {

            setIsUploading(false);

        }

    };

    // Proceed to application
    const handleProceed = () => {

        console.log("Proceed clicked");

        console.log("Passing bank data:", analysis?.financial_data);

        navigate("/apply", {
            state: {
                bankData: analysis?.financial_data
            }
        });

    };

    return (

        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-3xl mx-auto space-y-8"
        >

            <div>

                <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
                    Bank Statement Analysis
                </h1>

                <p className="text-neutral-500 mt-1">
                    Upload applicant's bank statement for automated financial extraction.
                </p>

            </div>

            <div className="bg-white p-8 rounded-3xl shadow-sm border border-neutral-100">

                {/* Upload UI */}

                {!analysis && (

                    <div className="space-y-6">

                        <div className="border-2 border-dashed border-neutral-200 rounded-2xl p-12 text-center hover:bg-neutral-50 transition-colors cursor-pointer relative">

                            <input
                                type="file"
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                onChange={handleFileChange}
                                accept=".pdf,.csv,.xlsx"
                            />

                            <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                <UploadCloud size={32}/>
                            </div>

                            <h3 className="text-lg font-medium text-neutral-900 mb-1">
                                {file ? file.name : "Click or drag file to upload"}
                            </h3>

                            <p className="text-sm text-neutral-500">
                                Supports PDF, CSV, Excel
                            </p>

                        </div>

                        {error && (
                            <p className="text-red-500 text-sm">{error}</p>
                        )}

                        <button
                            onClick={handleUpload}
                            disabled={!file || isUploading}
                            className="w-full bg-neutral-900 text-white py-3.5 rounded-xl font-medium disabled:opacity-50 hover:bg-neutral-800 transition-colors"
                        >

                            {isUploading ? "Analyzing..." : "Analyze Statement"}

                        </button>

                    </div>

                )}

                {/* Metrics UI */}

                {analysis && (

                    <div className="space-y-8">

                        <div className="flex items-center gap-4 p-4 bg-emerald-50 rounded-2xl text-emerald-800">

                            <CheckCircle2 size={24}/>

                            <div>

                                <h4 className="font-medium">
                                    Analysis Complete
                                </h4>

                                <p className="text-sm opacity-80">
                                    Extracted financial metrics
                                </p>

                            </div>

                        </div>

                        <div className="grid grid-cols-2 gap-4">

                            <Metric
                                title="Avg Monthly Income"
                                value={analysis?.financial_data?.avg_monthly_income || 0}
                            />

                            <Metric
                                title="Monthly Expenses"
                                value={analysis?.financial_data?.avg_monthly_expenses || 0}
                            />

                            <Metric
                                title="Savings Ratio"
                                value={
                                    analysis?.financial_data?.savings_ratio
                                        ? (analysis.financial_data.savings_ratio * 100).toFixed(1)
                                        : 0
                                }
                                suffix="%"
                            />

                            <Metric
                                title="Stability Score"
                                value={analysis?.financial_data?.financial_stability_score || 0}
                            />

                        </div>

                        <button
                            onClick={handleProceed}
                            className="w-full bg-emerald-500 text-white py-3.5 rounded-xl font-medium hover:bg-emerald-600 transition-colors flex items-center justify-center gap-2"
                        >

                            Proceed to Application <FileText size={18}/>

                        </button>

                    </div>

                )}

            </div>

        </motion.div>

    );

}


// Metric Card Component

function Metric({ title, value, suffix = "" }: any) {

    console.log("Metric render:", title, value);

    return (

        <div className="p-4 border border-neutral-100 rounded-xl bg-neutral-50">

            <p className="text-xs text-neutral-500 uppercase font-semibold mb-1">
                {title}
            </p>

            <p className="text-2xl font-mono text-neutral-900">
                {value}{suffix}
            </p>

        </div>

    );

}