import { useState } from 'react';
import { motion } from 'motion/react';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

export default function SecuritySettings() {
  const { user } = useAuth();
  const [otpPurpose, setOtpPurpose] = useState('mfa_login');
  const [otpCode, setOtpCode] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState('');

  const requestOtp = async () => {
    if (!user?.email) return;
    try {
      await authAPI.requestOtp(user.email, otpPurpose);
      setMessage('OTP sent to your verified email address.');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'OTP request failed');
    }
  };

  const verifyOtp = async () => {
    if (!user?.email || !otpCode) return;
    try {
      await authAPI.verifyOtp(user.email, otpCode, otpPurpose);
      setMessage('OTP verified successfully.');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'OTP verification failed');
    }
  };

  const toggleMfa = async (enable: boolean) => {
    if (!user?.email) return;
    try {
      await authAPI.configureMfa(user.email, enable);
      setMessage(enable ? 'MFA enabled' : 'MFA disabled');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'MFA update failed');
    }
  };

  const requestReset = async () => {
    if (!user?.email) return;
    try {
      await authAPI.requestPasswordReset(user.email);
      setMessage('Password reset token sent to your verified email address.');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Password reset request failed');
    }
  };

  const confirmReset = async () => {
    try {
      await authAPI.confirmPasswordReset(resetToken, newPassword);
      setMessage('Password reset successful.');
      setResetToken('');
      setNewPassword('');
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Password reset failed');
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900">Security Settings</h1>
        <p className="text-neutral-500 mt-1">OTP and reset tokens are sent only to your verified email address.</p>
      </div>

      <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">Email Delivery Help</p>
        <p className="mt-1">If you do not receive OTP/reset email, check inbox/spam and verify SMTP settings on backend.</p>
        <div className="mt-2 flex flex-wrap gap-3">
          <a href="https://mail.google.com" target="_blank" rel="noreferrer" className="underline">Open Gmail</a>
          <a href="https://outlook.live.com" target="_blank" rel="noreferrer" className="underline">Open Outlook</a>
          <a href="https://support.google.com/accounts/answer/185833" target="_blank" rel="noreferrer" className="underline">Gmail App Password Guide</a>
        </div>
      </div>

      <div className="bg-white border border-neutral-100 rounded-2xl p-6 space-y-6">
        <section className="space-y-3 rounded-xl border border-neutral-100 p-4">
          <h2 className="text-lg font-medium">1) Request OTP</h2>
          <div className="flex flex-col sm:flex-row gap-2">
            <select value={otpPurpose} onChange={(e) => setOtpPurpose(e.target.value)} className="px-3 py-2 border rounded-lg flex-1">
              <option value="mfa_login">MFA Login</option>
              <option value="login">Login</option>
            </select>
            <button onClick={requestOtp} className="px-3 py-2 rounded-lg bg-neutral-900 text-white">Send OTP to Email</button>
          </div>
          <div className="flex flex-col sm:flex-row gap-2">
            <input value={otpCode} onChange={(e) => setOtpCode(e.target.value)} placeholder="Enter OTP" className="px-3 py-2 border rounded-lg flex-1" />
            <button onClick={verifyOtp} className="px-3 py-2 rounded-lg bg-emerald-600 text-white">Verify OTP</button>
          </div>
        </section>

        <section className="space-y-3 rounded-xl border border-neutral-100 p-4">
          <h2 className="text-lg font-medium">2) MFA</h2>
          <div className="flex gap-2">
            <button onClick={() => toggleMfa(true)} className="px-3 py-2 rounded-lg bg-emerald-100 text-emerald-700">Enable MFA</button>
            <button onClick={() => toggleMfa(false)} className="px-3 py-2 rounded-lg bg-rose-100 text-rose-700">Disable MFA</button>
          </div>
        </section>

        <section className="space-y-3 rounded-xl border border-neutral-100 p-4">
          <h2 className="text-lg font-medium">3) Password Reset</h2>
          <button onClick={requestReset} className="px-3 py-2 rounded-lg bg-neutral-900 text-white">Request Reset Token</button>
          <input value={resetToken} onChange={(e) => setResetToken(e.target.value)} placeholder="Reset token" className="w-full px-3 py-2 border rounded-lg" />
          <input value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New password" type="password" className="w-full px-3 py-2 border rounded-lg" />
          <button onClick={confirmReset} className="px-3 py-2 rounded-lg bg-indigo-600 text-white">Confirm Password Reset</button>
        </section>

        {message && <p className="text-sm text-indigo-700">{message}</p>}
      </div>
    </motion.div>
  );
}

