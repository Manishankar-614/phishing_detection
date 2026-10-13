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

export interface AdminStats {
  total_scans: number;
  phishing_blocked: number;
  legitimate_allowed: number;
  suspicious_flagged: number;
  admin_corrections: number;
  pending_retraining: number;
  estimated_accuracy: number;
  model_version: string;
  last_retrained: string;
  total_retrained_samples: number;
  timeline_trends: Array<{
    date: string;
    legitimate: number;
    phishing: number;
    suspicious: number;
    total: number;
  }>;
  risk_bands: {
    low_0_35: number;
    med_35_65: number;
    high_65_100: number;
  };
  average_scores: {
    bert_email: number;
    cnn_url: number;
    isolation_forest_behavior: number;
  };
}

export interface AdminScanItem {
  id: string;
  timestamp: string;
  url: string;
  email: string;
  target: string;
  classification: "legitimate" | "phishing" | "suspicious" | string;
  risk_level: string;
  risk_score: number;
  risk_percentage: number;
  email_score: number;
  url_score: number;
  behavior_score: number;
  source: string;
  feedback?: {
    original_label: string;
    corrected_label: string;
    reason: string;
    admin: string;
    corrected_at: string;
    retrained: boolean;
  } | null;
}

export interface RetrainingLog {
  retraining_id: string;
  timestamp: string;
  samples_processed: number;
  loss_before: number;
  loss_after: number;
  loss_reduction_percent: string;
  accuracy_improvement: string;
  previous_version: string;
  new_version: string;
  epochs: number;
  batch_size: number;
  optimizer: string;
  status: string;
}

export interface RetrainingResponse {
  status: string;
  message: string;
  retraining_log: RetrainingLog;
  updated_calibration: {
    version: string;
    last_retrained: string;
    total_retrained_samples: number;
  };
}

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

export const fetchAdminStats = async (): Promise<AdminStats> => {
  const response = await apiClient.get<{ status: string; stats: AdminStats }>("/admin/stats");
  return response.data.stats;
};

export const fetchAdminScans = async (params?: {
  filter?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; scans: AdminScanItem[] }> => {
  const response = await apiClient.get<{ status: string; data: { total: number; scans: AdminScanItem[] } }>(
    "/admin/scans",
    { params }
  );
  return response.data.data;
};

export const submitCorrection = async (payload: {
  scan_id: string;
  corrected_label: "legitimate" | "phishing";
  reason?: string;
  admin?: string;
}): Promise<{ status: string; message: string }> => {
  const response = await apiClient.post<{ status: string; message: string }>(
    "/admin/correct",
    payload
  );
  return response.data;
};

export const triggerRetraining = async (): Promise<RetrainingResponse> => {
  const response = await apiClient.post<RetrainingResponse>("/admin/retrain");
  return response.data;
};

export interface BenchmarkResponse {
  status: string;
  test_dataset: string;
  sample_count: number;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    false_positive_rate: number;
    false_negative_rate: number;
  };
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
  ensemble_weights: {
    bert_weight: number;
    url_weight: number;
    behavior_weight: number;
  };
}

export const fetchBenchmark = async (): Promise<BenchmarkResponse> => {
  const response = await apiClient.get<BenchmarkResponse>("/admin/benchmark");
  return response.data;
};

export default apiClient;