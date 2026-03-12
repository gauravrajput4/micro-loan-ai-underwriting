import { Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'motion/react';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import Application from './pages/Application';
import BankUpload from './pages/BankUpload';
import Results from './pages/Results';
import EmiCalculator from './pages/EmiCalculator';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <AuthProvider>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="admin" element={<AdminDashboard />} />
            <Route path="apply" element={<Application />} />
            <Route path="upload" element={<BankUpload />} />
            <Route path="results" element={<Results />} />
            <Route path="calculator" element={<EmiCalculator />} />
          </Route>
        </Routes>
      </AnimatePresence>
    </AuthProvider>
  );
}
