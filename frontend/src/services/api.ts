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
    user_type: 'student' | 'unemployed' | 'admin';
    phone?: string;
}

export interface User {
    email: string;
    full_name: string;
    user_type: string;
}

export const authAPI = {
    login: async (data: LoginData) => {
        const response = await api.post('/auth/login', data);
        return response.data;
    },

    register: async (data: RegisterData) => {
        const response = await api.post('/auth/register', data);
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