import React, { useState } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, ArrowRight, User, Moon, Sun } from 'lucide-react';
import { authAPI, LoginData, RegisterData } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [isSignUp, setIsSignUp] = useState(false);
  const [userType, setUserType] = useState<'applicant' | 'student'>('applicant');
  const [loading, setLoading] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  const [error, setError] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupOtp, setSignupOtp] = useState('');
  const [signupOtpSent, setSignupOtpSent] = useState(false);
  const [signupOtpVerified, setSignupOtpVerified] = useState(false);

  const handleSignupRequestOtp = async () => {
    if (!signupEmail) {
      setError('Enter email first to request OTP.');
      return;
    }

    setOtpLoading(true);
    setError('');
    try {
      await authAPI.signupRequestOtp(signupEmail);
      setSignupOtpSent(true);
      setSignupOtpVerified(false);
      setError('OTP sent to your email. Please verify before signing up.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send signup OTP');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleSignupVerifyOtp = async () => {
    if (!signupEmail || !signupOtp) {
      setError('Enter email and OTP.');
      return;
    }

    setOtpLoading(true);
    setError('');
    try {
      await authAPI.signupVerifyOtp(signupEmail, signupOtp);
      setSignupOtpVerified(true);
      setError('Email verified. You can now create account.');
    } catch (err: any) {
      setSignupOtpVerified(false);
      setError(err.response?.data?.detail || 'Invalid OTP');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const formData = new FormData(e.currentTarget);
    
    try {
      if (isSignUp) {
        if (!signupOtpVerified) {
          setError('Please verify your email OTP before registration.');
          setLoading(false);
          return;
        }

        const registerData: RegisterData = {
          email: formData.get('email') as string,
          password: formData.get('password') as string,
          full_name: formData.get('fullName') as string,
          user_type: userType,
          phone: formData.get('phone') as string || '',
        };
        
        await authAPI.register(registerData);
        setIsSignUp(false);
        setError('Registration successful! Please login.');
      } else {
        const loginData: LoginData = {
          email: formData.get('email') as string,
          password: formData.get('password') as string,
        };
        
        const response = await authAPI.login(loginData);
        login(response.access_token, response.refresh_token, {
          email: response.email,
          full_name: response.full_name,
          user_type: response.user_type,
        });
        
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4 sm:p-6 font-sans relative">
      <button
        onClick={toggleTheme}
        className="absolute right-4 top-4 sm:right-6 sm:top-6 p-2.5 rounded-lg border border-neutral-200 bg-white/80 backdrop-blur hover:bg-neutral-100"
        aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 bg-white rounded-3xl shadow-xl overflow-hidden">

        {/* Left Side - Branding */}
        <div className="bg-neutral-900 p-8 sm:p-10 lg:p-12 flex flex-col justify-between relative overflow-hidden text-white min-h-[260px]">
          <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl translate-y-1/3 -translate-x-1/3"></div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-12">
              <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
                <GraduationCap size={24} className="text-white" />
              </div>
              <span className="font-semibold text-2xl tracking-tight">LoanMint</span>
            </div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-3xl sm:text-4xl lg:text-5xl font-medium leading-tight mb-6"
            >
              Fair financing<br/>for your<br/>education.
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-neutral-400 text-lg max-w-sm"
            >
              AI-powered personal loans for students and unemployed individuals, with transparent decisions.
            </motion.p>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="p-6 sm:p-8 lg:p-12 flex flex-col justify-center">
          <div className="max-w-md w-full mx-auto">
            <h2 className="text-2xl font-semibold mb-2">
              {isSignUp ? 'Create your account' : 'Welcome back'}
            </h2>
            <p className="text-neutral-500 mb-8">
              {isSignUp ? 'Join LoanMint to apply for your loan.' : 'Sign in to manage your loan application.'}
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
                  {error}
                </div>
              )}

              {isSignUp && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Full Name</label>
                  <input 
                    name="fullName"
                    type="text" 
                    placeholder="Jane Doe"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
                    required={isSignUp}
                  />
                </motion.div>
              )}

              {isSignUp && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">Phone Number</label>
                  <input 
                    name="phone"
                    type="tel" 
                    placeholder="+1 (555) 123-4567"
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
                  />
                </motion.div>
              )}

              {isSignUp && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                  <label className="block text-sm font-medium text-neutral-700 mb-1.5">User Type</label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { value: 'applicant', icon: User, label: 'Applicant' },
                      { value: 'student', icon: GraduationCap, label: 'Student' }
                    ].map(({ value, icon: Icon, label }) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setUserType(value as any)}
                        className={`p-3 rounded-lg border-2 transition-all flex flex-col items-center gap-1 ${
                          userType === value 
                            ? 'border-emerald-500 bg-emerald-50 text-emerald-700' 
                            : 'border-neutral-200 hover:border-neutral-300'
                        }`}
                      >
                        <Icon size={20} />
                        <span className="text-xs font-medium">{label}</span>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1.5">Email</label>
                <input 
                  name="email"
                  type="email" 
                  placeholder="user@example.com"
                  value={signupEmail}
                  onChange={(e) => {
                    setSignupEmail(e.target.value);
                    if (isSignUp) {
                      setSignupOtpVerified(false);
                    }
                  }}
                  className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
                  required
                />
              </div>

              {isSignUp && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="space-y-2">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Enter signup OTP"
                      value={signupOtp}
                      onChange={(e) => setSignupOtp(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
                    />
                    <button
                      type="button"
                      onClick={handleSignupRequestOtp}
                      disabled={otpLoading || !signupEmail}
                      className="px-4 rounded-xl border border-neutral-200 text-sm font-medium hover:bg-neutral-50 disabled:opacity-50"
                    >
                      Send OTP
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <button
                      type="button"
                      onClick={handleSignupVerifyOtp}
                      disabled={otpLoading || !signupOtpSent || !signupOtp}
                      className="px-4 py-2 rounded-lg bg-emerald-100 text-emerald-700 text-sm font-medium hover:bg-emerald-200 disabled:opacity-50"
                    >
                      Verify OTP
                    </button>
                    <span className={`text-xs font-medium ${signupOtpVerified ? 'text-emerald-600' : 'text-neutral-500'}`}>
                      {signupOtpVerified ? 'Email verified' : 'Verification pending'}
                    </span>
                  </div>
                </motion.div>
              )}

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1.5">Password</label>
                <input 
                  name="password"
                  type="password" 
                  placeholder="••••••••"
                  className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
                  required
                />
              </div>

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                type="submit"
                disabled={loading}
                className="w-full bg-neutral-900 text-white py-3.5 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-neutral-800 transition-colors mt-4 disabled:opacity-50"
              >
                {loading ? 'Loading...' : (isSignUp ? 'Sign Up' : 'Sign In')} 
                {!loading && <ArrowRight size={18} />}
              </motion.button>
            </form>

            <div className="mt-8 text-center text-sm text-neutral-500">
              {isSignUp ? 'Already have an account?' : 'Need an account?'}
              <button 
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setSignupOtp('');
                  setSignupOtpSent(false);
                  setSignupOtpVerified(false);
                  setError('');
                }}
                className="ml-2 text-emerald-600 font-medium hover:underline"
              >
                {isSignUp ? 'Sign In' : 'Sign Up'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
