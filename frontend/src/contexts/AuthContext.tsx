import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, login as loginApi, register as registerApi, logout as logoutApi, getUserProfile } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email_address: string, password: string) => Promise<void>;
  register: (data: {
    email_address: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      if (storedToken && storedUser) {
        try {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          // Verify token is still valid
          await getUserProfile();
        } catch (error) {
          // Token is invalid, clear storage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email_address: string, password: string) => {
    try {
      const response = await loginApi({ email_address, password });
      setUser(response.user);
      setToken(response.token);
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    } catch (error) {
      throw error;
    }
  };

  const register = async (data: {
    email_address: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
  }) => {
    try {
      const response = await registerApi(data);

      setUser(response.user);

      setToken(response.token);

      localStorage.setItem('token', response.token);

      localStorage.setItem('user', JSON.stringify(response.user));
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await logoutApi();
    } catch (error) {
      // Even if logout fails on server, clear local state
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user && !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};