import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Shared refresh token concurrency guard ──
// Prevents multiple concurrent refresh calls (which would trigger theft-detection
// and revoke ALL tokens when rotation is enabled).
let isRefreshing = false;
let pendingRequests: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function onRefreshed(newToken: string) {
  pendingRequests.forEach(({ resolve }) => resolve(newToken));
  pendingRequests = [];
}

function onRefreshFailed(err: unknown) {
  pendingRequests.forEach(({ reject }) => reject(err));
  pendingRequests = [];
}

/**
 * Perform a single refresh token call, shared by both the axios interceptor
 * and fetchWithAuth. If a refresh is already in progress, waits for it.
 */
async function refreshToken(): Promise<string> {
  const refreshTokenValue =
    typeof window !== "undefined"
      ? localStorage.getItem("refresh_token")
      : null;

  if (!refreshTokenValue) {
    throw new Error("No refresh token available");
  }

  // If another caller is already refreshing, queue behind it
  if (isRefreshing) {
    return new Promise<string>((resolve, reject) => {
      pendingRequests.push({ resolve, reject });
    });
  }

  isRefreshing = true;

  try {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await axios.post(`${baseURL}/api/auth/refresh`, {
      refresh_token: refreshTokenValue,
    });

    const newAccessToken = res.data.access_token;
    const newRefreshToken = res.data.refresh_token;

    localStorage.setItem("token", newAccessToken);
    localStorage.setItem("refresh_token", newRefreshToken);

    onRefreshed(newAccessToken);
    return newAccessToken;
  } catch (err) {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    onRefreshFailed(err);
    throw err;
  } finally {
    isRefreshing = false;
  }
}

// ── Axios response interceptor ──

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 非 401 或已经尝试过 refresh → 直接失败
    if (error.response?.status !== 401 || originalRequest._retry) {
      if (error.response?.status === 401) {
        logout();
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const newToken = await refreshToken();
      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return api(originalRequest);
    } catch (refreshErr) {
      logout();
      return Promise.reject(refreshErr);
    }
  },
);

// ── Public helpers ──

export function setTokens(accessToken: string, refreshToken: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  }
}

/**
 * 登出：先通知后端吊销 refresh token，再清除本地存储并跳转。
 * 即使后端调用失败，也始终清除本地状态（保证用户能退出）。
 */
export async function logout() {
  if (typeof window === "undefined") return;

  const accessToken = localStorage.getItem("token");
  const refreshTokenValue = localStorage.getItem("refresh_token");

  // 尝试通知后端吊销 token
  if (accessToken) {
    try {
      const baseURL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await axios.post(
        `${baseURL}/api/auth/logout`,
        { refresh_token: refreshTokenValue },
        { headers: { Authorization: `Bearer ${accessToken}` } },
      );
    } catch {
      // 后端调用失败不影响本地登出（token 过期、网络错误等）
    }
  }

  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

/**
 * 带 refresh token 自动刷新能力的原生 fetch 调用。
 * 用于 SSE 流式请求和文件下载等不走 axios 的场景。
 * 与 axios interceptor 共享同一个 refresh 并发锁，避免多个并发 refresh
 * 触发 token 轮换的盗用检测。
 */
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    try {
      const newToken = await refreshToken();

      // 用新 token 重试原请求
      headers.set("Authorization", `Bearer ${newToken}`);
      response = await fetch(url, { ...options, headers });
    } catch {
      logout();
      throw new Error("认证过期，请重新登录");
    }
  }

  return response;
}

export default api;
