// hooks/use-auth.ts
import { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  plan: 'Free' | 'Pro' | 'Enterprise';
  createdAt: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false
  });

  useEffect(() => {
    // Kiểm tra xem user đã đăng nhập chưa
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Kiểm tra token trong localStorage
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setAuthState({ user: null, isLoading: false, isAuthenticated: false });
        return;
      }

      // Gọi API để lấy thông tin user
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setAuthState({
          user: userData,
          isLoading: false,
          isAuthenticated: true
        });
      } else {
        // Token không hợp lệ
        localStorage.removeItem('auth_token');
        setAuthState({ user: null, isLoading: false, isAuthenticated: false });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuthState({ user: null, isLoading: false, isAuthenticated: false });
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const { token, user } = await response.json();
        localStorage.setItem('auth_token', token);
        setAuthState({
          user,
          isLoading: false,
          isAuthenticated: true
        });
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.message };
      }
    } catch (error) {
      return { success: false, error: 'Login failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setAuthState({
      user: null,
      isLoading: false,
      isAuthenticated: false
    });
  };

  const updateUser = (updatedUser: Partial<User>) => {
    if (authState.user) {
      setAuthState(prev => ({
        ...prev,
        user: { ...prev.user!, ...updatedUser }
      }));
    }
  };

  return {
    user: authState.user,
    isLoading: authState.isLoading,
    isAuthenticated: authState.isAuthenticated,
    login,
    logout,
    updateUser,
    checkAuthStatus
  };
}