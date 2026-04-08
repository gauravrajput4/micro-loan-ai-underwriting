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
import KycVerification from './pages/KycVerification';
import LoanQueue from './pages/LoanQueue';
import AuditViewer from './pages/AuditViewer';
import SecuritySettings from './pages/SecuritySettings';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './contexts/ThemeContext';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="admin" element={<ProtectedRoute allowedRoles={["admin", "underwriter", "risk_manager", "auditor"]}><AdminDashboard /></ProtectedRoute>} />
              <Route path="apply" element={<Application />} />
              <Route path="upload" element={<BankUpload />} />
              <Route path="results" element={<Results />} />
              <Route path="calculator" element={<EmiCalculator />} />
              <Route path="kyc" element={<KycVerification />} />
              <Route path="cases" element={<ProtectedRoute allowedRoles={["underwriter", "risk_manager", "admin"]}><LoanQueue /></ProtectedRoute>} />
              <Route path="audit" element={<ProtectedRoute allowedRoles={["auditor", "admin", "risk_manager"]}><AuditViewer /></ProtectedRoute>} />
              <Route path="security" element={<SecuritySettings />} />
            </Route>
          </Routes>
        </AnimatePresence>
      </AuthProvider>
    </ThemeProvider>
  );
}
