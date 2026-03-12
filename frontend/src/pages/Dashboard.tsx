import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Navigate } from 'react-router-dom';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

import {
    Calendar,
    Activity,
    CreditCard,
    IndianRupee
} from 'lucide-react';

import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI } from '@/src/services/api';

export default function Dashboard() {

    const { user } = useAuth();

    const [metrics, setMetrics] = useState<any>(null);

    if (user?.user_type === 'admin') {
        return <Navigate to="/admin" replace />;
    }

    useEffect(() => {

        if (!user?.email) return;

        dashboardAPI
            .getUserDashboard(user.email)
            .then(res => setMetrics(res))
            .catch(console.error);

    }, [user]);



    const repaymentData = metrics?.repaymentSchedule || [];



    const StatCard = ({ title, value, icon: Icon, subtitle, color }: any) => (

        <motion.div
            whileHover={{ y: -4 }}
            className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100"
        >

            <div className="flex justify-between items-start mb-4">

                <div className={`p-3 rounded-xl ${color}`}>
                    <Icon size={20} />
                </div>

            </div>

            <h3 className="text-neutral-500 text-sm font-medium mb-1">
                {title}
            </h3>

            <p className="text-3xl font-semibold text-neutral-900">
                {value}
            </p>

            {subtitle && (
                <p className="text-xs text-neutral-400 mt-2">
                    {subtitle}
                </p>
            )}

        </motion.div>
    );



    return (

        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
        >

            <div>

                <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">
                    My Dashboard
                </h1>

                <p className="text-neutral-500 mt-1">
                    Welcome back! Here is your current loan and financial status.
                </p>

            </div>



            {/* Stat Cards */}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

                <StatCard
                    title="Total Borrowed"
                    value={`₹${metrics?.totalBorrowed || 0}`}
                    icon={IndianRupee}
                    subtitle="Active Loan"
                    color="bg-blue-50 text-blue-600"
                />

                <StatCard
                    title="Next Payment"
                    value={`₹${metrics?.nextPayment || 0}`}
                    icon={Calendar}
                    subtitle="Upcoming EMI"
                    color="bg-emerald-50 text-emerald-600"
                />

                <StatCard
                    title="Credit Score"
                    value={metrics?.creditScore || 0}
                    icon={Activity}
                    subtitle="Generated Score"
                    color="bg-purple-50 text-purple-600"
                />



                <StatCard
                    title="Application Status"
                    value={metrics?.recentStatus || "No Application"}
                    icon={CreditCard}
                    subtitle="Latest Decision"
                    color="bg-neutral-100 text-neutral-600"
                />

            </div>



            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Repayment Chart */}

                <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">

                    <h3 className="text-lg font-semibold mb-6">
                        Estimated Repayment Schedule
                    </h3>

                    <div className="h-72">

                        <ResponsiveContainer width="100%" height="100%">

                            <AreaChart data={repaymentData}>

                                <defs>

                                    <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">

                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>

                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>

                                    </linearGradient>

                                </defs>

                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f5f5f5" />

                                <XAxis dataKey="month" />

                                <YAxis />

                                <Tooltip />

                                <Area
                                    type="monotone"
                                    dataKey="balance"
                                    stroke="#10b981"
                                    fill="url(#colorBalance)"
                                />

                            </AreaChart>

                        </ResponsiveContainer>

                    </div>

                </div>



                {/* Applications */}

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-100">

                    <h3 className="text-lg font-semibold mb-6">
                        My Applications
                    </h3>

                    <div className="space-y-4">

                        {metrics?.myApplications?.length > 0 ? (

                            metrics.myApplications.map((app: any, i: number) => (

                                <div
                                    key={i}
                                    className="flex items-center justify-between p-3 hover:bg-neutral-50 rounded-xl"
                                >

                                    <div>

                                        <p className="font-medium text-sm text-neutral-900">
                                            {app.loan_purpose}
                                        </p>

                                        <p className="text-xs text-neutral-500 font-mono mt-0.5">
                                            {new Date(app.created_at).toLocaleDateString()}
                                        </p>

                                    </div>

                                    <div className="text-right">

                                        <p className="font-medium text-sm text-neutral-900">
                                            ₹{app.loan_amount}
                                        </p>

                                    </div>

                                </div>

                            ))

                        ) : (

                            <p className="text-sm text-neutral-500 text-center py-4">
                                No recent applications.
                            </p>

                        )}

                    </div>

                </div>

            </div>

        </motion.div>

    );
}