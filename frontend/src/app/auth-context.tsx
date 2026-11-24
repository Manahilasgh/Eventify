
"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";

import api, {
  setAuthToken,
  clearAuthTokens,
  getAuthToken,
} from "@/lib/api";

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "customer" | "organizer";
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const response = await api.get("/api/auth/me/");
    setUser(response.data);
  }, []);

  const logout = useCallback(() => {
    clearAuthTokens();
    setUser(null);
  }, []);

  // Restore authentication when the application loads
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (
          getAuthToken() ||
          localStorage.getItem("eventify_refresh_token")
        ) {
          await refreshUser();
        }
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    };

    const handleExpired = () => logout();

    window.addEventListener("auth:expired", handleExpired);

    initializeAuth();

    return () => {
      window.removeEventListener(
        "auth:expired",
        handleExpired
      );
    };
  }, [refreshUser, logout]);

  const login = async (
    email: string,
    password: string
  ) => {
    const response = await api.post("/api/auth/login/", {
      email,
      password,
    });

    const { access, refresh } = response.data;

    setAuthToken(access);

    localStorage.setItem(
      "eventify_refresh_token",
      refresh
    );

    try {
      await refreshUser();
    } catch (error) {
      logout();
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    await api.post("/api/auth/register/", data);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}
