import axiosClient from "../services/axiosclient";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

// تعريف نوع بيانات المستخدم
interface User {
  id: string;
  username: string;
  email?: string;
  is_admin?: boolean;
}

// تعريف نوع سياق المصادقة
interface AuthContextType {
  token: string | null;
  user: User | null;
  setToken: (newToken: string) => void;
  setUser: (user: User | null) => void;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

// Create context with the defined type
const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  // حالة لتخزين توكن المصادقة
  const [token, setToken_] = useState<string | null>(localStorage.getItem("token"));
  // حالة لتخزين بيانات المستخدم - لا يتم تخزينها في localStorage
  const [user, setUser_] = useState<User | null>(null);

  // دالة لتعيين توكن المصادقة
  const setToken = (newToken: string | null) => {
    setToken_(newToken);
  };

  // دالة لتعيين بيانات المستخدم
  const setUser = (newUser: User | null) => {
    setUser_(newUser);
  };

  useEffect(() => {
    if (token) {
      axiosClient.defaults.headers.common["Authorization"] = "Bearer " + token;
      localStorage.setItem('token', token);
    } else {
      delete axiosClient.defaults.headers.common["Authorization"];
      localStorage.removeItem('token')
    }
  }, [token]);

  // استرجاع معلومات المستخدم من الخادم عند وجود توكن
  useEffect(() => {
    const fetchUserData = async () => {
      if (token && !user) {
        try {
          const response = await axiosClient.get('/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          setUser_(response.data);
        } catch (error) {
          console.error('Failed to fetch user data:', error);
          // إذا فشل الحصول على بيانات المستخدم، قم بتسجيل الخروج
          setToken(null);
        }
      }
    };
    
    fetchUserData();
  }, [token, user]);

  // دالة تسجيل الدخول
  const login = async (username: string, password: string) => {
    try {
      // استدعاء API لتسجيل الدخول باستخدام نقطة النهاية الجديدة
      const { loginUser } = await import('../services/api');
      const authResponse = await loginUser(username, password);
      
      // تعيين التوكن والمستخدم
      setToken(authResponse.access_token);
      // Asegurarse de que user no sea undefined
      if (authResponse.user) {
        setUser(authResponse.user);
      } else {
        // Crear un objeto de usuario a partir de los datos recibidos
        const user: User = {
          id: authResponse.user_id.toString(),
          username: authResponse.username,
          is_admin: authResponse.is_admin
        };
        setUser(user);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  // دالة تسجيل الخروج
  const logout = () => {
    setToken(null);
    setUser(null);
  };

  // قيمة سياق المصادقة المخزنة مؤقتًا
  const contextValue = useMemo(
    () => ({
      token,
      user,
      setToken,
      setUser,
      login,
      logout,
      isAuthenticated: !!token && !!user,
      isAdmin: !!user && user.is_admin === true
    }),
    [token, user]
  );

  // Provide the authentication context to the children components
  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthProvider;
