import axios from "axios";

// الحصول على عنوان API من متغيرات البيئة
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

console.log('API URL configured as:', API_URL);

// إنشاء مثيل axios مع الإعدادات الأساسية
const axiosClient = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
    // إضافة مهلة للطلبات
    timeout: 10000, // 10 ثواني
});

// اعتراض الطلبات للتسجيل والتشخيص
axiosClient.interceptors.request.use(
    config => {
        console.log(`Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
        return config;
    },
    error => {
        console.error('Request error:', error);
        return Promise.reject(error);
    }
);

// اعتراض الاستجابات للتسجيل والتشخيص
axiosClient.interceptors.response.use(
    response => {
        console.log(`Response: ${response.status} from ${response.config.url}`);
        return response;
    },
    error => {
        if (error.response) {
            console.error(`Response error: ${error.response.status} from ${error.config?.url}`);
            console.error('Response data:', error.response.data);
        } else if (error.request) {
            console.error('No response received:', error.request);
        } else {
            console.error('Error setting up request:', error.message);
        }
        return Promise.reject(error);
    }
);

export default axiosClient;
