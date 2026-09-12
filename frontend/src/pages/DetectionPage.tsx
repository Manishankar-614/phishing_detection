import React, { useEffect, useRef, useState } from "react";
import {
  Shield,
  ShieldCheck,
  Search,
  Activity,
  Zap,
  Mail,
  Globe,
  AlertTriangle,
  Copy,
  Check,
  RefreshCw,
  Sparkles,
  Server,
  Sliders,
  Terminal,
  Clock,
  Trash2,
} from "lucide-react";

import {
  analyzePhishing,
  checkApiHealth,
  type BehaviorData,
  type DetectionResult,
  ApiError,
} from "../services/api";

import BehaviorTracker from "../utils/BehaviorTracker";

// ============================================================
// PRESET SAMPLES FOR QUICK TESTING
// ============================================================
interface PresetSample {
  id: string;
  name: string;
  badge: string;
  badgeType: "danger" | "warning" | "success";
  email: string;
  url: string;
  description: string;
}

const PRESET_SAMPLES: PresetSample[] = [
  {
    id: "phish-bank",
    name: "Urgent Bank Account Verification",
    badge: "Phishing Attack",
    badgeType: "danger",
    email: `URGENT SECURITY ALERT: Unauthorized sign-in attempt detected on your Online Banking profile.

Dear Valued Customer,
We observed suspicious login attempts from an unknown IP address (Moscow, Russia). To safeguard your assets, your account access has been temporarily restricted.

You are required to verify your identity and confirm your account credentials within 24 hours to avoid permanent suspension.

Please click the secure verification link below immediately:
https://secure-login-portal-verify.bank-auth0-update.xyz/login

Thank you for your cooperation,
Fraud & Risk Mitigation Unit`,
    url: "https://secure-login-portal-verify.bank-auth0-update.xyz/login",
    description: "High-urgency credential harvester with typosquatting domain and threat of suspension.",
  },
  {
    id: "phish-invoice",
    name: "Fake Wire Transfer / Invoice Attached",
    badge: "Suspicious BEC",
    badgeType: "warning",
    email: `Subject: Overdue Invoice #INV-89241 - Immediate Payment Required

Good day,

Please find attached the revised invoice for last month's cloud infrastructure consulting services. The banking coordinates have been updated due to our mid-year audit.

Kindly process the outstanding balance of $14,850.00 to the updated account details via the remittance confirmation page:
http://billing-remittance-portal.co.vu/payment/inv-89241

Regards,
Financial Controller
Apex Enterprise Solutions`,
    url: "http://billing-remittance-portal.co.vu/payment/inv-89241",
    description: "Business Email Compromise (BEC) with anomalous payment link on free TLD (.vu).",
  },
  {
    id: "legit-github",
    name: "Legitimate GitHub Notification",
    badge: "Legitimate",
    badgeType: "success",
    email: `[GitHub] A new personal access token (classic) was generated for your account.

Hi @developer,

We noticed that a new personal access token was created from your browser session on Windows in California, USA.

If you generated this token, no further action is needed. If you did not create it, please review your authorized credentials immediately at:
https://github.com/settings/tokens

Thanks,
The GitHub Team`,
    url: "https://github.com/settings/tokens",
    description: "Authentic transactional security notice pointing to official verified domain.",
  },
];

interface ScanHistoryItem {
  id: string;
  timestamp: string;
  url: string;
  riskScore: number;
  classification: string;
  riskLevel: string;
}

export default function DetectionPage() {
  const [email, setEmail] = useState("");
  const [url, setUrl] = useState("");
  const [activeTab, setActiveTab] = useState<"hybrid" | "email" | "url">("hybrid");

  const [behavior, setBehavior] = useState<BehaviorData>({
    num_clicks: 0,
    time_on_page: 0,
    num_redirects: 0,
    failed_logins: 0,
    mouse_speed: 0,
    typing_speed: 0,
    tab_switches: 0,
  });

  const [manualBehaviorOverride, setManualBehaviorOverride] = useState(false);
  const [loading, setLoading] = useState(false);
  const [scanStep, setScanStep] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [copiedReport, setCopiedReport] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  // System Health
  const [apiStatus, setApiStatus] = useState<"online" | "checking" | "offline">("checking");
  const [apiLatency, setApiLatency] = useState<number | null>(null);

  const trackerRef = useRef<BehaviorTracker | null>(null);
  const resultsRef = useRef<HTMLDivElement | null>(null);

  // ==========================================================
  // 1. BEHAVIOR TRACKING & HEALTH CHECK
  // ==========================================================
  useEffect(() => {
    // Load history from localStorage
    try {
      const saved = localStorage.getItem("phishguard_history");
      if (saved) {
        setHistory(JSON.parse(saved));
      }
    } catch {
      // Ignore
    }

    // Start Live Behavior Tracker
    const tracker = new BehaviorTracker();
    trackerRef.current = tracker;

    const interval = setInterval(() => {
      if (!manualBehaviorOverride) {
        setBehavior(tracker.getBehavior());
      }
    }, 1000);

    // Initial Health Check
    checkHealth();

    return () => {
      clearInterval(interval);
      tracker.destroy();
      trackerRef.current = null;
    };
  }, [manualBehaviorOverride]);

  const checkHealth = async () => {
    setApiStatus("checking");
    const start = performance.now();
    try {
      await checkApiHealth();
      const duration = Math.round(performance.now() - start);
      setApiLatency(duration);
      setApiStatus("online");
    } catch {
      setApiStatus("offline");
      setApiLatency(null);
    }
  };

  // ==========================================================
  // 2. ANALYZE HANDLER
  // ==========================================================
  const handleAnalyze = async () => {
    setError("");

    if (activeTab === "hybrid" || activeTab === "email") {
      if (!email.trim()) {
        setError("Please enter the email content to inspect.");
        return;
      }
    }

    if (activeTab === "hybrid" || activeTab === "url") {
      if (!url.trim()) {
        setError("Please enter a target URL to analyze.");
        return;
      }
    }

    try {
      setLoading(true);
      setScanStep("Initializing Multi-Modal Inference Pipeline...");

      const timer1 = setTimeout(() => setScanStep("Running BERT Sequence Classification..."), 400);
      const timer2 = setTimeout(() => setScanStep("Scanning URL Subdomains & CNN Character Vectors..."), 900);
      const timer3 = setTimeout(() => setScanStep("Evaluating Behavioral Anomaly Distribution..."), 1400);
      const timer4 = setTimeout(() => setScanStep("Synthesizing Multi-Tier Risk Matrix & Attribution..."), 1900);

      const currentBehavior = manualBehaviorOverride
        ? behavior
        : trackerRef.current
        ? trackerRef.current.getBehavior()
        : behavior;

      const isEmailMode = activeTab === "email";

      const response = await analyzePhishing({
        email: email.trim(),
        url: url.trim(),
        behavior: currentBehavior,
        is_email_page: isEmailMode,
      });

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);

      if (response.result) {
        setResult(response.result);

        // Add to history
        const newItem: ScanHistoryItem = {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString(),
          url: url.trim() || "Email Context Only",
          riskScore: response.result.risk.risk_percentage,
          classification: response.result.risk.classification,
          riskLevel: response.result.risk.risk_level,
        };
        const updated = [newItem, ...history.slice(0, 9)];
        setHistory(updated);
        try {
          localStorage.setItem("phishguard_history", JSON.stringify(updated));
        } catch {
          // ignore
        }

        // Scroll to results
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      }
    } catch (err: unknown) {
      console.error(err);
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to connect to the PhishGuard AI detection backend.");
      }
    } finally {
      setLoading(false);
      setScanStep("");
    }
  };

  const loadPreset = (preset: PresetSample) => {
    setEmail(preset.email);
    setUrl(preset.url);
    setError("");
    setResult(null);
  };

  const clearForm = () => {
    setEmail("");
    setUrl("");
    setError("");
    setResult(null);
  };

  const copyReportToClipboard = () => {
    if (!result) return;
    const reportText = `[PhishGuard AI Threat Report]
Classification: ${result.risk.classification.toUpperCase()} (${result.risk.risk_percentage}% Risk)
Severity Level: ${result.risk.risk_level.toUpperCase()}
Recommended Action: ${result.risk.recommended_action}

Model Scores:
- BERT (Email Semantics): ${(result.email.email_score * 100).toFixed(1)}%
- CNN (URL Lexical/Structural): ${(result.url.url_score * 100).toFixed(1)}%
- Isolation Forest (Behavior Anomaly): ${(result.behavior.behavior_score * 100).toFixed(1)}%
- Fusion Consensus: ${(result.fusion.fused_score * 100).toFixed(1)}% (${result.fusion.model_agreement.agreement})

Summary:
${result.explanation.summary}

Key Indicators:
${result.explanation.reasons.map((r) => `- [${r.severity.toUpperCase()}] ${r.source}: ${r.reason}`).join("\n")}
`;
    navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem("phishguard_history");
  };

  return (
    <div className="detection-page">
      {/* ======================================================
          TOP NAVIGATION BAR
      ====================================================== */}
      <nav className="cyber-navbar">
        <div className="brand-badge">
          <div className="brand-icon-wrapper">
            <ShieldCheck className="brand-icon" size={26} />
            <div className="pulse-dot" />
          </div>
          <div className="brand-text">
            <div className="brand-title">
              PhishGuard <span className="highlight-ai">AI</span>
            </div>
            <div className="brand-subtitle">Multi-Modal Threat & Anomaly Engine</div>
          </div>
        </div>

        <div className="navbar-meta">
          <div
            className={`server-status-pill ${
              apiStatus === "online" ? "status-online" : apiStatus === "checking" ? "status-checking" : "status-offline"
            }`}
            onClick={checkHealth}
            title="Click to re-ping backend server"
          >
            <Server size={14} />
            <span>
              {apiStatus === "online"
                ? `Engine Online (${apiLatency ?? 0}ms)`
                : apiStatus === "checking"
                ? "Connecting..."
                : "Engine Offline"}
            </span>
            <span className="live-indicator" />
          </div>

          <div className="version-tag">v2.0 • BERT+CNN</div>
        </div>
      </nav>

      {/* ======================================================
          HERO BANNER & PRESETS
      ====================================================== */}
      <section className="hero-banner">
        <div className="hero-content">
          <h1>
            Enterprise-Grade <span className="gradient-text">Zero-Day Phishing</span> Defense
          </h1>
          <p>
            Combines Deep Transformer contextual NLP (BERT), Character-level Convolutional Neural Networks (CNN),
            and Behavioral Isolation Forest anomaly analysis for comprehensive threat assessment.
          </p>
        </div>

        {/* QUICK PRESETS */}
        <div className="presets-container">
          <div className="presets-label">
            <Sparkles size={16} className="sparkle-icon" />
            <span>Load Real-World Samples:</span>
          </div>
          <div className="presets-pills">
            {PRESET_SAMPLES.map((sample) => (
              <button
                key={sample.id}
                type="button"
                className={`preset-button preset-${sample.badgeType}`}
                onClick={() => loadPreset(sample)}
              >
                <span className="preset-name">{sample.name}</span>
                <span className={`preset-badge badge-${sample.badgeType}`}>{sample.badge}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ======================================================
          MAIN ANALYSIS CONSOLE
      ====================================================== */}
      <div className="console-layout">
        <div className="main-scanner-column">
          <section className="cyber-card input-card">
            {/* TABS */}
            <div className="tab-control-bar">
              <div className="tabs-wrapper">
                <button
                  type="button"
                  className={`tab-btn ${activeTab === "hybrid" ? "tab-active" : ""}`}
                  onClick={() => setActiveTab("hybrid")}
                >
                  <Zap size={16} />
                  <span>Hybrid Multi-Modal</span>
                </button>
                <button
                  type="button"
                  className={`tab-btn ${activeTab === "email" ? "tab-active" : ""}`}
                  onClick={() => setActiveTab("email")}
                >
                  <Mail size={16} />
                  <span>Email Content (BERT)</span>
                </button>
                <button
                  type="button"
                  className={`tab-btn ${activeTab === "url" ? "tab-active" : ""}`}
                  onClick={() => setActiveTab("url")}
                >
                  <Globe size={16} />
                  <span>URL Scanner (CNN)</span>
                </button>
              </div>

              {(email || url) && (
                <button type="button" className="clear-btn" onClick={clearForm} title="Reset fields">
                  Clear
                </button>
              )}
            </div>

            {/* INPUT FIELDS */}
            <div className="form-fields">
              {(activeTab === "hybrid" || activeTab === "email") && (
                <div className="input-group">
                  <div className="input-header">
                    <label htmlFor="emailInput">
                      <Mail size={16} className="field-icon" />
                      <span>Email Content / Message Headers</span>
                    </label>
                    <span className="char-counter">{email.length} chars</span>
                  </div>
                  <textarea
                    id="emailInput"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Paste the raw or body text of the suspicious email here (headers, subject, and body supported)..."
                    rows={8}
                  />
                </div>
              )}

              {(activeTab === "hybrid" || activeTab === "url") && (
                <div className="input-group">
                  <div className="input-header">
                    <label htmlFor="urlInput">
                      <Globe size={16} className="field-icon" />
                      <span>Target Suspicious URL / Domain</span>
                    </label>
                  </div>
                  <div className="url-input-wrapper">
                    <input
                      id="urlInput"
                      type="text"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="e.g. https://account-verification-portal.example.xyz/login"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* LIVE BEHAVIORAL SIGNALS */}
            <div className="telemetry-section">
              <div className="telemetry-header">
                <div className="telemetry-title">
                  <Activity size={18} className="telemetry-pulse-icon" />
                  <div>
                    <h3>Real-time Client Telemetry & Behavioral Signals</h3>
                    <p>Live interaction metrics fed to the Isolation Forest anomaly detector</p>
                  </div>
                </div>

                <button
                  type="button"
                  className={`override-toggle ${manualBehaviorOverride ? "active-override" : ""}`}
                  onClick={() => setManualBehaviorOverride(!manualBehaviorOverride)}
                >
                  <Sliders size={14} />
                  <span>{manualBehaviorOverride ? "Custom Override" : "Live Auto-Tracking"}</span>
                </button>
              </div>

              <div className="telemetry-grid">
                <TelemetryCard
                  label="Clicks"
                  value={behavior.num_clicks}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, num_clicks: v })}
                />
                <TelemetryCard
                  label="Dwell Time"
                  value={`${behavior.time_on_page}s`}
                  rawValue={behavior.time_on_page}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, time_on_page: v })}
                />
                <TelemetryCard
                  label="Mouse Velocity"
                  value={behavior.mouse_speed}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, mouse_speed: v })}
                />
                <TelemetryCard
                  label="Typing Speed"
                  value={behavior.typing_speed}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, typing_speed: v })}
                />
                <TelemetryCard
                  label="Tab Focus Switches"
                  value={behavior.tab_switches}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, tab_switches: v })}
                />
                <TelemetryCard
                  label="Redirect Count"
                  value={behavior.num_redirects}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, num_redirects: v })}
                />
                <TelemetryCard
                  label="Failed Logins"
                  value={behavior.failed_logins}
                  isEditable={manualBehaviorOverride}
                  onChange={(v) => setBehavior({ ...behavior, failed_logins: v })}
                />
              </div>
            </div>

            {/* ERROR ALERT */}
            {error && (
              <div className="cyber-alert alert-error">
                <AlertTriangle size={18} />
                <span>{error}</span>
              </div>
            )}

            {/* ANALYZE BUTTON */}
            <button
              type="button"
              className={`cyber-analyze-btn ${loading ? "btn-loading" : ""}`}
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? (
                <>
                  <RefreshCw size={20} className="spin-animation" />
                  <span>{scanStep || "Analyzing Threats..."}</span>
                </>
              ) : (
                <>
                  <Search size={20} />
                  <span>Execute Multi-Modal Threat Analysis</span>
                </>
              )}
            </button>
          </section>

          {/* ======================================================
              DETECTION RESULTS DISPLAY
          ====================================================== */}
          {result && (
            <div ref={resultsRef}>
              <ResultsDashboard
                result={result}
                copiedReport={copiedReport}
                onCopyReport={copyReportToClipboard}
                filterSeverity={filterSeverity}
                setFilterSeverity={setFilterSeverity}
              />
            </div>
          )}
        </div>

        {/* SIDEBAR: RECENT SCANS & MODEL ARCHITECTURE */}
        <aside className="sidebar-column">
          {/* RECENT SCAN HISTORY */}
          <div className="cyber-card history-card">
            <div className="card-header-bar">
              <div className="card-header-title">
                <Clock size={16} />
                <h3>Recent Scans</h3>
              </div>
              {history.length > 0 && (
                <button type="button" className="icon-subtle-btn" onClick={clearHistory} title="Clear history">
                  <Trash2 size={14} />
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div className="empty-history">
                <Shield size={24} className="empty-icon" />
                <p>No scans performed in this session.</p>
              </div>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-top">
                      <span className={`status-badge-small badge-${item.riskLevel}`}>{item.classification}</span>
                      <span className="history-time">{item.timestamp}</span>
                    </div>
                    <div className="history-url" title={item.url}>
                      {item.url}
                    </div>
                    <div className="history-meter">
                      <div
                        className={`history-fill fill-${item.riskLevel}`}
                        style={{ width: `${item.riskScore}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* PIPELINE ARCHITECTURE INFO */}
          <div className="cyber-card info-sidebar-card">
            <div className="card-header-title">
              <Terminal size={16} />
              <h3>AI Engine Architecture</h3>
            </div>
            <ul className="arch-list">
              <li>
                <div className="arch-badge">BERT Transformer</div>
                <p>Evaluates semantic deception, urgency, and coercive language in email bodies.</p>
              </li>
              <li>
                <div className="arch-badge">Character CNN</div>
                <p>Deep 1D Convolutional Neural Network analyzing raw URL lexical patterns & subdomains.</p>
              </li>
              <li>
                <div className="arch-badge">Isolation Forest</div>
                <p>Tree-based multivariate anomaly estimation on interaction and telemetry vectors.</p>
              </li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}

// ============================================================
// COMPONENT: TELEMETRY CARD
// ============================================================
function TelemetryCard({
  label,
  value,
  rawValue,
  isEditable,
  onChange,
}: {
  label: string;
  value: string | number;
  rawValue?: number;
  isEditable: boolean;
  onChange: (val: number) => void;
}) {
  return (
    <div className="telemetry-card">
      <div className="telemetry-label">{label}</div>
      {isEditable ? (
        <input
          type="number"
          className="telemetry-input"
          value={typeof value === "number" ? value : rawValue ?? 0}
          onChange={(e) => onChange(Number(e.target.value))}
        />
      ) : (
        <div className="telemetry-val-display">{value}</div>
      )}
    </div>
  );
}

// ============================================================
// COMPONENT: RESULTS DASHBOARD
// ============================================================
function ResultsDashboard({
  result,
  copiedReport,
  onCopyReport,
  filterSeverity,
  setFilterSeverity,
}: {
  result: DetectionResult;
  copiedReport: boolean;
  onCopyReport: () => void;
  filterSeverity: string;
  setFilterSeverity: (sev: string) => void;
}) {
  const { risk, email, url, behavior, fusion, explanation } = result;

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "critical":
        return "#f43f5e";
      case "high":
        return "#f97316";
      case "medium":
        return "#eab308";
      default:
        return "#10b981";
    }
  };

  const filteredReasons =
    filterSeverity === "all"
      ? explanation.reasons
      : explanation.reasons.filter((r) => r.severity.toLowerCase() === filterSeverity.toLowerCase());

  return (
    <section className="results-container">
      {/* 1. MASTER VERDICT BANNER */}
      <div className={`verdict-banner verdict-${risk.risk_level.toLowerCase()}`}>
        <div className="verdict-gauge-wrapper">
          <svg className="circular-gauge" viewBox="0 0 120 120">
            <circle className="gauge-bg" cx="60" cy="60" r="50" />
            <circle
              className="gauge-progress"
              cx="60"
              cy="60"
              r="50"
              stroke={getRiskColor(risk.risk_level)}
              strokeDasharray={314.159}
              strokeDashoffset={314.159 - (314.159 * risk.risk_percentage) / 100}
            />
          </svg>
          <div className="gauge-center">
            <span className="gauge-number">{risk.risk_percentage}%</span>
            <span className="gauge-sub">RISK</span>
          </div>
        </div>

        <div className="verdict-text-block">
          <div className="verdict-level-pill">
            {risk.risk_level.toUpperCase()} THREAT LEVEL
          </div>
          <h2 className="verdict-classification">
            {risk.classification.toUpperCase()}
          </h2>
          <p className="verdict-action">
            <strong>Recommended Action:</strong> {risk.recommended_action}
          </p>
        </div>

        <div className="verdict-actions-block">
          <div className="confidence-chip">
            <Sparkles size={14} />
            <span>{risk.confidence_percentage}% Model Confidence</span>
          </div>
          <button type="button" className="copy-report-btn" onClick={onCopyReport}>
            {copiedReport ? <Check size={16} /> : <Copy size={16} />}
            <span>{copiedReport ? "Report Copied!" : "Export Threat Report"}</span>
          </button>
        </div>
      </div>

      {/* 2. ENSEMBLE MODEL METRICS */}
      <div className="metrics-grid">
        <ModelScoreCard
          title="BERT Context Model"
          subtitle="Email NLP Semantics"
          icon={<Mail size={20} />}
          score={email.email_score}
          tag="Transformer"
        />
        <ModelScoreCard
          title="Deep CNN Classifier"
          subtitle="URL Lexical Vectors"
          icon={<Globe size={20} />}
          score={url.url_score}
          tag="1D Convolution"
        />
        <ModelScoreCard
          title="Isolation Forest"
          subtitle="Behavioral Anomaly"
          icon={<Activity size={20} />}
          score={behavior.behavior_score}
          tag="Anomaly Forest"
        />
      </div>

      {/* 3. FUSION CONSENSUS METRIC */}
      <div className="fusion-summary-card">
        <div className="fusion-left">
          <Zap className="fusion-icon" size={24} />
          <div>
            <h4>Dynamic Feature Fusion Score</h4>
            <p>
              Consensus Agreement: <strong>{fusion.model_agreement.agreement}</strong>
            </p>
          </div>
        </div>
        <div className="fusion-score">
          {(fusion.fused_score * 100).toFixed(1)}%
        </div>
      </div>

      {/* 4. EXPLAINABILITY & ATTRIBUTION INTELLIGENCE */}
      <div className="cyber-card explanation-container">
        <div className="explanation-header-bar">
          <div>
            <h3>Explainability & Risk Attribution</h3>
            <p className="summary-text">{explanation.summary}</p>
          </div>

          <div className="severity-filter-bar">
            <span className="filter-label">Filter:</span>
            {["all", "critical", "high", "medium", "low"].map((sev) => (
              <button
                key={sev}
                type="button"
                className={`filter-pill ${filterSeverity === sev ? "active-filter" : ""}`}
                onClick={() => setFilterSeverity(sev)}
              >
                {sev.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="attribution-list">
          {filteredReasons.length === 0 ? (
            <div className="empty-reasons">No indicators matched the selected filter.</div>
          ) : (
            filteredReasons.map((item, idx) => (
              <div key={idx} className={`reason-box reason-${item.severity.toLowerCase()}`}>
                <div className="reason-top-row">
                  <div className="reason-source-badge">
                    {item.source === "email" ? <Mail size={13} /> : item.source === "url" ? <Globe size={13} /> : <Activity size={13} />}
                    <span>{item.source.toUpperCase()}</span>
                  </div>
                  <span className={`reason-sev-pill sev-${item.severity.toLowerCase()}`}>
                    {item.severity.toUpperCase()}
                  </span>
                </div>
                <p className="reason-text">{item.reason}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}

// ============================================================
// COMPONENT: MODEL SCORE CARD
// ============================================================
function ModelScoreCard({
  title,
  subtitle,
  icon,
  score,
  tag,
}: {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  score: number;
  tag: string;
}) {
  const percentage = (score * 100).toFixed(1);
  const isHighRisk = score >= 0.7;
  const isMedRisk = score >= 0.4 && score < 0.7;

  const barColor = isHighRisk ? "#f43f5e" : isMedRisk ? "#eab308" : "#10b981";

  return (
    <div className="model-score-card">
      <div className="model-card-top">
        <div className="model-card-icon">{icon}</div>
        <span className="model-tag">{tag}</span>
      </div>

      <div className="model-card-info">
        <h4>{title}</h4>
        <p>{subtitle}</p>
      </div>

      <div className="model-score-display">
        <span className="score-val" style={{ color: barColor }}>
          {percentage}%
        </span>
        <span className="score-label">Phishing Probability</span>
      </div>

      <div className="score-progress-bar">
        <div
          className="score-progress-fill"
          style={{ width: `${percentage}%`, backgroundColor: barColor }}
        />
      </div>
    </div>
  );
}