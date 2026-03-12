import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";
import { motion } from "motion/react";

interface Props {
    score: number;
}

export default function CreditScoreGauge({ score }: Props) {

    const normalized = (score / 850) * 100;

    const data = [
        {
            name: "score",
            value: normalized,
            fill:
                score >= 750
                    ? "#10b981"
                    : score >= 650
                        ? "#3b82f6"
                        : score >= 550
                            ? "#f59e0b"
                            : "#ef4444"
        }
    ];

    const getRating = () => {
        if (score >= 750) return "Excellent";
        if (score >= 650) return "Good";
        if (score >= 550) return "Fair";
        return "Poor";
    };

    return (
        <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100"
        >

            <h3 className="text-lg font-semibold mb-4">
                Credit Score
            </h3>

            <div className="h-48">

                <ResponsiveContainer width="100%" height="100%">

                    <RadialBarChart
                        innerRadius="70%"
                        outerRadius="100%"
                        data={data}
                        startAngle={180}
                        endAngle={0}
                    >

                        <PolarAngleAxis
                            type="number"
                            domain={[0, 100]}
                            angleAxisId={0}
                            tick={false}
                        />

                        <RadialBar
                            background
                            dataKey="value"
                            cornerRadius={10}
                        />

                    </RadialBarChart>

                </ResponsiveContainer>

            </div>

            <div className="text-center -mt-6">

                <p className="text-3xl font-semibold text-neutral-900">
                    {score}
                </p>

                <p className="text-sm text-neutral-500">
                    {getRating()}
                </p>

            </div>

        </motion.div>
    );
}