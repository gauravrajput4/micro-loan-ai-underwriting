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
    IndianRupee,
    CheckCircle2
} from 'lucide-react';

import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI } from '@/src/services/api';

export default function Dashboard() {

    const { user } = useAuth();

    const [metrics, setMetrics] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    const normalizeStatus = (value?: string) => {
        const status = (value || '').toLowerCase();
        if (status.includes('approve')) return 'Approved';
        if (status.includes('reject')) return 'Rejected';
        if (status.includes('pending')) return 'Pending';
        return 'No Application';
    };

    const getStatusBadgeClasses = (status: string) => {
        if (status === 'Approved') return 'bg-emerald-100 text-emerald-700';
        if (status === 'Rejected') return 'bg-rose-100 text-rose-700';
        if (status === 'Pending') return 'bg-amber-100 text-amber-700';
        return 'bg-neutral-100 text-neutral-600';
    };

    if (['admin', 'underwriter', 'risk_manager', 'auditor'].includes((user?.user_type || '').toLowerCase())) {
        return <Navigate to="/admin" replace />;
    }

    useEffect(() => {

        if (!user?.email) return;

        dashboardAPI
            .getUserDashboard(user.email)
            .then(res => {
                setMetrics(res);
                setLoadError(null);
            })
            .catch((err) => {
                console.error(err);
                setLoadError('Unable to load dashboard data. Please refresh.');
            })
            .finally(() => setIsLoading(false));

    }, [user]);



    const repaymentData = metrics?.repaymentSchedule || [];
    const latestStatus = normalizeStatus(metrics?.recentStatus);

    if (isLoading) {
        return <div className="text-sm text-neutral-500">Loading dashboard...</div>;
    }

    if (loadError) {
        return <div className="text-sm text-rose-600">{loadError}</div>;
    }



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
                    value={latestStatus}
                    icon={CreditCard}
                    subtitle="Latest Decision"
                    color={
                        latestStatus === 'Approved'
                            ? 'bg-emerald-50 text-emerald-600'
                            : latestStatus === 'Rejected'
                                ? 'bg-rose-50 text-rose-600'
                                : latestStatus === 'Pending'
                                    ? 'bg-amber-50 text-amber-600'
                                    : 'bg-neutral-100 text-neutral-600'
                    }
                />
            </div>

            {latestStatus === 'Approved' && (
                <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 flex items-center gap-3">
                    <CheckCircle2 size={20} className="text-emerald-600" />
                    <div>
                        <p className="font-semibold text-emerald-800">Loan Approved</p>
                        <p className="text-sm text-emerald-700">
                            Your latest loan request has been approved.
                        </p>
                    </div>
                </div>
            )}



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

                                        <span className={`inline-flex mt-1 px-2 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClasses(normalizeStatus(app.status === 'pending' && i === 0 ? metrics?.recentStatus : app.status))}`}>
                                            {normalizeStatus(app.status === 'pending' && i === 0 ? metrics?.recentStatus : app.status)}
                                        </span>

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