import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';
import type { User, LoginRequest, LoginResponse, ApiResponse } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: !!localStorage.getItem('access_token'),
      isLoading: false,
      error: null,

      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post<ApiResponse<LoginResponse>>('/users/login', credentials);
          const { access_token, refresh_token } = response.data.data;

          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          // Fetch user info after login
          const userResponse = await api.get<ApiResponse<User>>('/users/me');
          set({
            user: userResponse.data.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Login failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
      },

      fetchUser: async () => {
        if (!localStorage.getItem('access_token')) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const response = await api.get<ApiResponse<User>>('/users/me');
          set({
            user: response.data.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated }),
    }
  )
);
