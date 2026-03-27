import React, { useEffect, useState } from "react";
import { motion } from "motion/react";
import { useAuth } from "../contexts/AuthContext";

import {
    Shield,
    User,
    TrendingUp,
    Users,
    DollarSign,
    CheckCircle
} from "lucide-react";

import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    ResponsiveContainer
} from "recharts";

import { dashboardAPI } from "../services/api";

export default function AdminDashboard() {

    const { user } = useAuth();

    const [stats,setStats] = useState<any[]>([]);
    const [recentApplications,setRecentApplications] = useState<any[]>([]);
    const [creditDistribution,setCreditDistribution] = useState<any[]>([]);
    const [monthlyTrends,setMonthlyTrends] = useState<any[]>([]);
    const [statusDistribution,setStatusDistribution] = useState<any>({});

    const normalizeStatus = (app: any) => {
        if (typeof app?.prediction === 'number') {
            return app.prediction === 1 ? 'Approved' : 'Rejected';
        }

        const raw = String(app?.status || app?.decision || '').toLowerCase();
        if (raw.includes('approve')) return 'Approved';
        if (raw.includes('reject')) return 'Rejected';
        if (raw.includes('pending')) return 'Pending';
        return 'Pending';
    };

    const statusBadgeClass = (status: string) => {
        if (status === 'Approved') return 'bg-green-100 text-green-800';
        if (status === 'Rejected') return 'bg-red-100 text-red-800';
        return 'bg-amber-100 text-amber-800';
    };

    useEffect(()=>{

        dashboardAPI.getAdminDashboard().then(data=>{

            const summary = data.summary;

            setStats([
                {
                    label:"Total Applications",
                    value:summary.total_applications,
                    icon:Users,
                    color:"bg-blue-500"
                },
                {
                    label:"Approved Loans",
                    value:summary.approved_loans,
                    icon:CheckCircle,
                    color:"bg-green-500"
                },
                {
                    label:"Total Predictions",
                    value:summary.total_predictions,
                    icon:DollarSign,
                    color:"bg-purple-500"
                },
                {
                    label:"Success Rate",
                    value:`${summary.approval_rate}%`,
                    icon:TrendingUp,
                    color:"bg-orange-500"
                }
            ]);

            setRecentApplications(data.recent_applications);
            setCreditDistribution(data.credit_score_distribution);
            setMonthlyTrends(data.monthly_trends);
            setStatusDistribution(data.status_distribution);

        });

    },[]);

    return (

        <div className="px-4 sm:px-6 lg:px-8 py-6 max-w-7xl mx-auto space-y-8">

            {/* Header */}

            <div className="flex items-center gap-3">

                <Shield className="text-blue-600" size={32}/>

                <div>

                    <h1 className="text-3xl font-bold text-gray-900">
                        Admin Dashboard
                    </h1>

                    <p className="text-gray-600">
                        Welcome back, {user?.full_name}
                    </p>

                </div>

            </div>

            {/* Stats */}

            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">

                {stats.map((stat,index)=>(
                    <motion.div
                        key={stat.label}
                        initial={{opacity:0,y:20}}
                        animate={{opacity:1,y:0}}
                        transition={{delay:index*0.1}}
                        className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
                    >

                        <div className="flex justify-between">

                            <div>

                                <p className="text-gray-600 text-sm font-medium">
                                    {stat.label}
                                </p>

                                <p className="text-2xl font-bold mt-1">
                                    {stat.value}
                                </p>

                            </div>

                            <div className={`${stat.color} p-3 rounded-lg`}>
                                <stat.icon className="text-white" size={22}/>
                            </div>

                        </div>

                    </motion.div>
                ))}

            </div>

            {/* Charts */}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Loan Approval Trend */}

                <motion.div className="bg-white p-6 rounded-xl shadow-sm border">

                    <h3 className="text-lg font-semibold mb-6">
                        Loan Approval Trend
                    </h3>

                    <div className="h-64">

                        <ResponsiveContainer width="100%" height="100%">

                            <LineChart data={monthlyTrends}>

                                <CartesianGrid strokeDasharray="3 3"/>

                                <XAxis dataKey="_id.month"/>

                                <YAxis/>

                                <Tooltip/>

                                <Line dataKey="approved" stroke="#10b981" strokeWidth={3}/>

                                <Line dataKey="total" stroke="#6366f1" strokeWidth={3}/>

                            </LineChart>

                        </ResponsiveContainer>

                    </div>

                </motion.div>

                {/* Credit Score Distribution */}

                <motion.div className="bg-white p-6 rounded-xl shadow-sm border">

                    <h3 className="text-lg font-semibold mb-6">
                        Credit Score Distribution
                    </h3>

                    <div className="h-64">

                        <ResponsiveContainer width="100%" height="100%">

                            <BarChart data={creditDistribution}>

                                <CartesianGrid strokeDasharray="3 3"/>

                                <XAxis dataKey="range"/>

                                <YAxis/>

                                <Tooltip/>

                                <Bar dataKey="count" fill="#6366f1" radius={[8,8,0,0]}/>

                            </BarChart>

                        </ResponsiveContainer>

                    </div>

                </motion.div>

                {/* Risk Heatmap */}

                <motion.div className="bg-white p-6 rounded-xl shadow-sm border">

                    <h3 className="text-lg font-semibold mb-6">
                        Risk Distribution
                    </h3>

                    <div className="h-64">

                        <ResponsiveContainer width="100%" height="100%">

                            <PieChart>

                                <Pie
                                    data={[
                                        {name:"Approved",value:statusDistribution.approved},
                                        {name:"Rejected",value:statusDistribution.rejected}
                                    ]}
                                    dataKey="value"
                                    outerRadius={90}
                                >

                                    <Cell fill="#10b981"/>
                                    <Cell fill="#ef4444"/>

                                </Pie>

                                <Tooltip/>

                            </PieChart>

                        </ResponsiveContainer>

                    </div>

                </motion.div>

                {/* Monthly Predictions */}

                <motion.div className="bg-white p-6 rounded-xl shadow-sm border">

                    <h3 className="text-lg font-semibold mb-6">
                        Monthly Predictions
                    </h3>

                    <div className="h-64">

                        <ResponsiveContainer width="100%" height="100%">

                            <BarChart data={monthlyTrends}>

                                <CartesianGrid strokeDasharray="3 3"/>

                                <XAxis dataKey="_id.month"/>

                                <YAxis/>

                                <Tooltip/>

                                <Bar dataKey="total" fill="#3b82f6" radius={[8,8,0,0]}/>

                            </BarChart>

                        </ResponsiveContainer>

                    </div>

                </motion.div>

            </div>

            {/* Recent Applications */}

            <motion.div className="bg-white rounded-xl shadow-sm border">

                <div className="p-6 border-b">

                    <h2 className="text-xl font-semibold">
                        Recent Applications
                    </h2>

                </div>

                <div className="overflow-x-auto">

                    <table className="w-full">

                        <thead className="bg-gray-50">

                        <tr>

                            <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                                Applicant
                            </th>

                            <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                                Credit Score
                            </th>

                            <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                                Probability
                            </th>

                            <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                                Status
                            </th>

                        </tr>

                        </thead>

                        <tbody className="divide-y">

                        {recentApplications.map((app:any)=>{

                            const status = normalizeStatus(app);
                            const probability = Number(app?.probability || 0);

                            return(

                                <tr key={app._id} className={status === 'Approved' ? 'bg-green-50/40' : ''}>

                                    <td className="px-6 py-4 flex items-center gap-3">

                                        <User size={20}/>

                                        <span>{app.email}</span>

                                    </td>

                                    <td className="px-6 py-4">
                                        {app.credit_score}
                                    </td>

                                    <td className="px-6 py-4">
                                        {(probability * 100).toFixed(1)}%
                                    </td>

                                    <td className="px-6 py-4">

                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusBadgeClass(status)}`}>

                                        {status}

                                        </span>

                                    </td>

                                </tr>
                            );
                        })}
                        </tbody>
                    </table>
                </div>
            </motion.div>
        </div>
    );

}