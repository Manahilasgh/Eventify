
import axios, { InternalAxiosRequestConfig } from "axios";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

interface RetryConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

export const getAuthToken = () => {
  if (typeof window === "undefined") return null;

  return localStorage.getItem("eventify_token");
};

export const setAuthToken = (token: string | null) => {
  if (typeof window === "undefined") return;

  if (token) {
    localStorage.setItem("eventify_token", token);
  } else {
    localStorage.removeItem("eventify_token");
  }
};

export const clearAuthTokens = () => {
  if (typeof window === "undefined") return;

  localStorage.removeItem("eventify_token");
  localStorage.removeItem("eventify_refresh_token");
};

// Attach access token to each request
api.interceptors.request.use((config) => {
  const token = getAuthToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Share one refresh request between concurrent requests
let refreshPromise: Promise<string> | null = null;

const refreshAccessToken = async (): Promise<string> => {
  const refreshToken = localStorage.getItem(
    "eventify_refresh_token"
  );

  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  const response = await axios.post(
    `${apiBaseUrl}/api/auth/refresh/`,
    { refresh: refreshToken }
  );

  const accessToken = response.data.access;

  setAuthToken(accessToken);

  if (response.data.refresh) {
    localStorage.setItem(
      "eventify_refresh_token",
      response.data.refresh
    );
  }

  return accessToken;
};

// Refresh expired access tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as
      | RetryConfig
      | undefined;

    if (
      typeof window === "undefined" ||
      !originalRequest ||
      error.response?.status !== 401 ||
      originalRequest._retry ||
      originalRequest.url?.includes("/api/auth/login/") ||
      originalRequest.url?.includes("/api/auth/register/") ||
      originalRequest.url?.includes("/api/auth/refresh/")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const newToken = await refreshPromise;

      originalRequest.headers.Authorization =
        `Bearer ${newToken}`;

      return api(originalRequest);
    } catch (refreshError) {
      clearAuthTokens();

      window.dispatchEvent(new Event("auth:expired"));

      return Promise.reject(refreshError);
    }
  }
);

export default api;
