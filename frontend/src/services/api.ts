import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attach token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

export interface LoginData {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    full_name: string;
    user_type: 'applicant' | 'student' | 'unemployed' | 'underwriter' | 'risk_manager' | 'admin' | 'auditor';
    phone?: string;
}

export interface User {
    email: string;
    full_name: string;
    user_type: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user_type: string;
    full_name: string;
    email: string;
}

export const authAPI = {
    login: async (data: LoginData) => {
        const response = await api.post<LoginResponse>('/auth/login', data);
        return response.data;
    },

    register: async (data: RegisterData) => {
        const response = await api.post('/auth/register', data);
        return response.data;
    },

    signupRequestOtp: async (email: string) => {
        const response = await api.post('/auth/signup/request-otp', { email });
        return response.data;
    },

    signupVerifyOtp: async (email: string, code: string) => {
        const response = await api.post('/auth/signup/verify-otp', { email, code });
        return response.data;
    },

    refresh: async (refreshToken: string) => {
        const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
        return response.data;
    },

    logout: async (refreshToken: string) => {
        const response = await api.post('/auth/logout', { refresh_token: refreshToken });
        return response.data;
    },

    requestOtp: async (email: string, purpose: string) => {
        const response = await api.post('/auth/otp/request', { email, purpose });
        return response.data;
    },

    verifyOtp: async (email: string, code: string, purpose: string) => {
        const response = await api.post('/auth/otp/verify', { email, code, purpose });
        return response.data;
    },

    requestPasswordReset: async (email: string) => {
        const response = await api.post('/auth/password-reset/request', { email });
        return response.data;
    },

    confirmPasswordReset: async (token: string, newPassword: string) => {
        const response = await api.post('/auth/password-reset/confirm', { token, new_password: newPassword });
        return response.data;
    },

    configureMfa: async (email: string, enable: boolean) => {
        const response = await api.post('/auth/mfa/config', { email, enable });
        return response.data;
    },
};

export const loanAPI = {
    submitApplication: async (data: any) => {
        const response = await api.post('/loan/apply', data);
        return response.data;
    },

    getApplications: async () => {
        const response = await api.get('/loan/applications');
        return response.data;
    },

    calculateEMI: async (data: any) => {
        const response = await api.post('/loan/calculate-emi', data);
        return response.data;
    },
};


export const dashboardAPI = {

    getUserDashboard: async (email: string) => {
        const response = await api.get('/dashboard/metrics', {
            params: { email: (email || '').trim().toLowerCase() },
        });
        return response.data;
    },

    getAdminDashboard: async () => {
        const response = await api.get('/dashboard/admin-dashboard');
        return response.data;
    }

};

export const kycAPI = {
    uploadDocument: async (loanId: string, docType: string, docNumber: string, file: File) => {
        const formData = new FormData();
        formData.append('loan_id', loanId);
        formData.append('doc_type', docType);
        formData.append('doc_number', docNumber);
        formData.append('file', file);
        const response = await api.post('/kyc/documents', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    uploadSelfie: async (loanId: string, file: File) => {
        const formData = new FormData();
        formData.append('loan_id', loanId);
        formData.append('file', file);
        const response = await api.post('/kyc/selfie', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    verifyLiveness: async (loanId: string, blinkScore: number, faceMatchScore: number) => {
        const response = await api.post(`/kyc/liveness/verify?loan_id=${loanId}`, {
            blink_score: blinkScore,
            face_match_score: faceMatchScore,
        });
        return response.data;
    },

    getStatus: async (loanId: string) => {
        const response = await api.get(`/kyc/status/${loanId}`);
        return response.data;
    },

    review: async (loanId: string, status: string, notes?: string) => {
        const response = await api.post(`/kyc/review/${loanId}`, { status, notes });
        return response.data;
    },
};

export const workflowAPI = {
    myCases: async () => {
        const response = await api.get('/workflow/cases/my');
        return response.data;
    },

    transition: async (loanId: string, toStatus: string, comment?: string) => {
        const response = await api.post(`/workflow/cases/${loanId}/transition`, {
            to_status: toStatus,
            comment,
        });
        return response.data;
    },

    decide: async (loanId: string, decision: 'approved' | 'rejected', reason: string) => {
        const response = await api.post(`/workflow/cases/${loanId}/decision`, {
            decision,
            reason,
        });
        return response.data;
    },

    overrideDecision: async (loanId: string, fromDecision: string, toDecision: string, reason: string) => {
        const response = await api.post('/workflow/cases/override', {
            loan_id: loanId,
            from_decision: fromDecision,
            to_decision: toDecision,
            reason,
        });
        return response.data;
    },
};

export const auditAPI = {
    listEvents: async (limit = 100) => {
        const response = await api.get(`/audit/events?limit=${limit}`);
        return response.data;
    },

    loanEvents: async (loanId: string) => {
        const response = await api.get(`/audit/loan/${loanId}`);
        return response.data;
    },
};

// ⭐ Bank statement upload API
export const uploadAPI = {
    uploadBankStatement: async (email: string, file: File) => {

        const formData = new FormData();

        formData.append("email", email);
        formData.append("file", file);

        const response = await api.post(
            "/upload/upload-bank-statement",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        return response.data;
    },
};

export default api;