import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig } from "axios";

// ----------------------------------------------------------------------
// 1. ENVIRONMENT CONFIGURATION
// ----------------------------------------------------------------------
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";

// ----------------------------------------------------------------------
// 2. DOMAIN & DTO TYPE DEFINITIONS
// ----------------------------------------------------------------------
export interface BehaviorData {
  num_clicks: number;
  time_on_page: number;
  num_redirects: number;
  failed_logins: number;
  mouse_speed: number;
  typing_speed: number;
  tab_switches: number;
}

export interface AnalyzeRequest {
  email?: string;
  url?: string;
  behavior: BehaviorData;
  is_email_page?: boolean;
  email_urls?: string[];
  email_links?: Array<{ text: string; href: string }>;
}

export interface EmailModelResult {
  email_score: number;
  [key: string]: unknown;
}

export interface UrlModelResult {
  url_score: number;
  [key: string]: unknown;
}

export interface BehaviorModelResult {
  behavior_score: number;
  is_anomaly?: boolean;
  [key: string]: unknown;
}

export interface FusionResult {
  fused_score: number;
  model_agreement: {
    agreement: string;
    score_variance?: number;
  };
}

export interface RiskResult {
  risk_score: number;
  risk_percentage: number;
  risk_level: "low" | "medium" | "high" | "critical" | string;
  classification: "legitimate" | "suspicious" | "phishing" | string;
  confidence_percentage: number;
  recommended_action: string;
}

export interface ReasonItem {
  source: "email" | "url" | "behavior" | "system" | string;
  severity: "low" | "medium" | "high" | "critical" | string;
  reason: string;
}

export interface ExplanationResult {
  summary: string;
  reasons: ReasonItem[];
}

export interface DetectionResult {
  email: EmailModelResult;
  url: UrlModelResult;
  behavior: BehaviorModelResult;
  fusion: FusionResult;
  risk: RiskResult;
  explanation: ExplanationResult;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  result?: T;
  message?: string;
}

export interface HealthCheckResponse {
  status: string;
  message: string;
}

// ----------------------------------------------------------------------
// 3. CUSTOM ERROR CLASS FOR CLIENT-SIDE HANDLING
// ----------------------------------------------------------------------
export class ApiError extends Error {
  statusCode?: number;
  details?: unknown;

  constructor(message: string, statusCode?: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.details = details;
  }
}

// ----------------------------------------------------------------------
// 4. AXIOS CLIENT FACTORY & INTERCEPTORS
// ----------------------------------------------------------------------
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  timeout: 60000,
});

// Request Interceptor: Attach Auth tokens if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Standardized Error Normalization
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message?: string }>) => {
    const message =
      error.response?.data?.message ||
      (error.code === "ECONNABORTED"
        ? "Request timed out during AI model analysis."
        : error.message || "An unexpected network error occurred.");

    return Promise.reject(
      new ApiError(message, error.response?.status, error.response?.data)
    );
  }
);

// ----------------------------------------------------------------------
// 5. SERVICE METHODS
// ----------------------------------------------------------------------
export const analyzePhishing = async (
  payload: AnalyzeRequest,
  config?: AxiosRequestConfig
): Promise<ApiResponse<DetectionResult>> => {
  const response = await apiClient.post<ApiResponse<DetectionResult>>(
    "/analyze",
    payload,
    config
  );
  return response.data;
};

export const checkApiHealth = async (
  config?: AxiosRequestConfig
): Promise<HealthCheckResponse> => {
  const response = await apiClient.get<HealthCheckResponse>("/health", config);
  return response.data;
};

export default apiClient;