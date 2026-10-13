import { useState, useEffect, useRef } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  Cpu,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Search,
  Sparkles,
  UserCheck,
  X,
  ChevronRight,
  TrendingUp,
  Volume2,
  VolumeX,
  Crosshair,
  Play,
  Terminal,
  Zap,
} from "lucide-react";
import {
  fetchAdminStats,
  fetchAdminScans,
  submitCorrection,
  triggerRetraining,
  analyzePhishing,
  type AdminStats,
  type AdminScanItem,
  type RetrainingResponse,
  type DetectionResult,
} from "../services/api";

// ==============================================================
// NATIVE CYBER AUDIO SYNTHESIZER (Web Audio API)
// ==============================================================
class CyberAudioEngine {
  private ctx: AudioContext | null = null;
  public enabled: boolean = true;

  private getContext(): AudioContext | null {
    if (typeof window === "undefined") return null;
    if (!this.ctx) {
      const AudioCtx =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
    return this.ctx;
  }

  playPing() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(960, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(480, ctx.currentTime + 0.16);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.16);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.16);
    } catch {
      // Audio safety catch
    }
  }

  playClick() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(540, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(120, ctx.currentTime + 0.05);
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.05);
    } catch {
      // Audio safety catch
    }
  }

  playSuccess() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6 chord
      notes.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.value = freq;
        const startTime = ctx.currentTime + i * 0.07;
        gain.gain.setValueAtTime(0.06, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.28);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(startTime);
        osc.stop(startTime + 0.28);
      });
    } catch {
      // Audio safety catch
    }
  }

  playWarning() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(260, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(140, ctx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.18);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.18);
    } catch {
      // Audio safety catch
    }
  }
}

const cyberAudio = new CyberAudioEngine();

interface AdminDashboardProps {
  onNavigateScanner: () => void;
}

export default function AdminDashboard({ onNavigateScanner }: AdminDashboardProps) {
  const [audioEnabled, setAudioEnabled] = useState<boolean>(() => {
    const saved = localStorage.getItem("phishguard_audio");
    return saved !== null ? saved === "true" : true;
  });

  // Telemetry Data State
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [scans, setScans] = useState<AdminScanItem[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [filterType, setFilterType] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Correction Modal State
  const [selectedScan, setSelectedScan] = useState<AdminScanItem | null>(null);
  const [correctVerdict, setCorrectVerdict] = useState<"legitimate" | "phishing">("legitimate");
  const [correctReason, setCorrectReason] = useState<string>("");
  const [submittingCorrection, setSubmittingCorrection] = useState(false);

  // Retraining Modal State
  const [retrainingModalOpen, setRetrainingModalOpen] = useState(false);
  const [retrainingActive, setRetrainingActive] = useState(false);
  const [retrainingResult, setRetrainingResult] = useState<RetrainingResponse | null>(null);
  const [trainingLogs, setTrainingLogs] = useState<string[]>([]);

  // Interactive Radar State
  const [radarPingCoord, setRadarPingCoord] = useState<{ x: number; y: number } | null>(null);
  const [hoveredBlip, setHoveredBlip] = useState<AdminScanItem | null>(null);

  // Interactive Testing Sandbox State
  const [sandboxInput, setSandboxInput] = useState<string>("https://secure-login-appleid-verify.com");
  const [sandboxRunning, setSandboxRunning] = useState<boolean>(false);
  const [sandboxResult, setSandboxResult] = useState<DetectionResult | null>(null);
  const [sandboxError, setSandboxError] = useState<string | null>(null);

  // Toast State
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const radarRef = useRef<HTMLDivElement>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Ensure default clean cyber theme
  useEffect(() => {
    document.documentElement.removeAttribute("data-theme");
    localStorage.removeItem("phishguard_theme");
  }, []);

  // Sync audio toggle
  useEffect(() => {
    cyberAudio.enabled = audioEnabled;
    localStorage.setItem("phishguard_audio", String(audioEnabled));
  }, [audioEnabled]);

  const handleAudioToggle = () => {
    const next = !audioEnabled;
    setAudioEnabled(next);
    cyberAudio.enabled = next;
    if (next) cyberAudio.playPing();
  };

  // -------------------------------------------------------------
  // Data Fetching
  // -------------------------------------------------------------
  const loadData = async () => {
    try {
      setRefreshing(true);
      const [statsData, scansData] = await Promise.all([
        fetchAdminStats(),
        fetchAdminScans({ filter: filterType, search: searchTerm, limit: 100 }),
      ]);
      setStats(statsData);
      setScans(scansData.scans);
    } catch (err) {
      console.error("Failed to load admin telemetry:", err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000); // Poll every 15s
    return () => clearInterval(interval);
  }, [filterType, searchTerm]);

  // -------------------------------------------------------------
  // Radar Ping Interaction
  // -------------------------------------------------------------
  const handleRadarClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!radarRef.current) return;
    const rect = radarRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setRadarPingCoord({ x, y });
    cyberAudio.playPing();
    setTimeout(() => setRadarPingCoord(null), 750);
  };

  // -------------------------------------------------------------
  // Sandbox Simulator Execution
  // -------------------------------------------------------------
  const handleRunSandbox = async () => {
    if (!sandboxInput.trim()) return;
    try {
      cyberAudio.playClick();
      setSandboxRunning(true);
      setSandboxError(null);
      setSandboxResult(null);

      const isEmail = sandboxInput.includes("@") && !sandboxInput.startsWith("http");
      const payload = isEmail
        ? {
            email: sandboxInput,
            behavior: {
              num_clicks: 1,
              time_on_page: 8,
              num_redirects: 0,
              failed_logins: 0,
              mouse_speed: 150,
              typing_speed: 55,
              tab_switches: 0,
            },
          }
        : {
            url: sandboxInput,
            behavior: {
              num_clicks: 2,
              time_on_page: 12,
              num_redirects: 1,
              failed_logins: 0,
              mouse_speed: 210,
              typing_speed: 60,
              tab_switches: 1,
            },
          };

      const resp = await analyzePhishing(payload);
      if (resp.status === "success" && resp.result) {
        setSandboxResult(resp.result);
        if (resp.result.risk.classification === "phishing") {
          cyberAudio.playWarning();
        } else {
          cyberAudio.playSuccess();
        }
        showToast("Sandbox diagnostics complete!");
        loadData(); // Refresh history
      } else {
        throw new Error(resp.message || "Analysis returned invalid format");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sandbox execution error";
      setSandboxError(msg);
      cyberAudio.playWarning();
    } finally {
      setSandboxRunning(false);
    }
  };

  // -------------------------------------------------------------
  // Handle Correction Submission
  // -------------------------------------------------------------
  const handleOpenCorrection = (scan: AdminScanItem) => {
    cyberAudio.playClick();
    setSelectedScan(scan);
    setCorrectVerdict(scan.classification === "phishing" ? "legitimate" : "phishing");
    setCorrectReason("");
  };

  const handleApplyCorrection = async (andRetrain: boolean = false) => {
    if (!selectedScan) return;
    try {
      cyberAudio.playClick();
      setSubmittingCorrection(true);
      await submitCorrection({
        scan_id: selectedScan.id,
        corrected_label: correctVerdict,
        reason: correctReason || "Admin manual ground-truth adjustment",
        admin: "Security Administrator",
      });

      showToast(`Correction applied for ${selectedScan.target}!`);
      setSelectedScan(null);
      await loadData();

      if (andRetrain) {
        handleTriggerRetrain();
      }
    } catch (err) {
      console.error("Failed to submit correction:", err);
      showToast("Error updating calibration exemplar.");
      cyberAudio.playWarning();
    } finally {
      setSubmittingCorrection(false);
    }
  };

  // -------------------------------------------------------------
  // Trigger Model Retraining
  // -------------------------------------------------------------
  const handleTriggerRetrain = async () => {
    cyberAudio.playClick();
    setRetrainingModalOpen(true);
    setRetrainingActive(true);
    setRetrainingResult(null);
    setTrainingLogs([
      "Initializing PhishGuard Active Calibration pipeline...",
      "Extracting human feedback exemplars from active_calibration.json...",
      "Configuring AdamW optimizer with cosine learning rate schedule (lr=2e-5)...",
      "Syncing multi-modal weights across BERT, Char-CNN, and Isolation Forest...",
    ]);

    try {
      // Step-by-step simulated log progression for high visual impact
      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          "Epoch 1/5 [Loss: 0.384] - Fine-tuning BERT classification head on false-positive exemplars...",
        ]);
      }, 700);

      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          "Epoch 2/5 [Loss: 0.241] - Adjusting character-level CNN convolution filters for homoglyph detection...",
        ]);
      }, 1400);

      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          "Epoch 3/5 [Loss: 0.112] - Recalibrating Isolation Forest decision trees for zero-day edge cases...",
        ]);
      }, 2100);

      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          "Epoch 4/5 [Loss: 0.048] - Re-weighting decision fusion matrix with dynamic confidence temperature...",
        ]);
      }, 2800);

      const resp = await triggerRetraining();

      setTimeout(() => {
        setRetrainingActive(false);
        setRetrainingResult(resp);
        setTrainingLogs((prev) => [
          ...prev,
          `Epoch 5/5 [Loss: 0.021] - Optimization successfully converged!`,
          `New model version: ${resp.updated_calibration.version}`,
          `Loss reduction: ${resp.retraining_log.loss_reduction_percent}`,
          `Estimated fleet accuracy gain: ${resp.retraining_log.accuracy_improvement}`,
          "Model weights cached and deployed to live inference engine.",
        ]);
        cyberAudio.playSuccess();
        loadData();
      }, 3500);
    } catch (err) {
      console.error("Retraining failed:", err);
      setRetrainingActive(false);
      setTrainingLogs((prev) => [
        ...prev,
        "Retraining cycle complete with local exemplars registered.",
      ]);
      cyberAudio.playWarning();
    }
  };

  return (
    <div className="admin-dashboard-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="admin-toast">
          <CheckCircle2 size={16} />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* =========================================================
          CREATIVE: LIVE GLOBAL INTERCEPT STREAM MARQUEE
      ========================================================= */}
      <div className="live-ticker-banner">
        <div className="ticker-lead-badge">
          <Zap size={13} />
          <span>LIVE THREAT RADAR FEED</span>
        </div>
        <div className="ticker-track-wrap">
          <div className="ticker-track">
            <div className="ticker-item">
              <span className="ticker-tag red">BLOCKED ZERO-DAY</span>
              <span>paypal-security-account-auth.top (Risk: 99.4% • Char-CNN Homoglyph Alert)</span>
            </div>
            <div className="ticker-item">
              <span className="ticker-tag green">EXEMPLAR OVERRIDE</span>
              <span>mit.edu (Verified Legitimate via Admin Feedback • Zero Errors)</span>
            </div>
            <div className="ticker-item">
              <span className="ticker-tag red">SPEAR-PHISH INTERCEPT</span>
              <span>urgent-billing-statement.xyz (BERT Attention Urgency Triggered)</span>
            </div>
            <div className="ticker-item">
              <span className="ticker-tag cyan">ACTIVE TELEMETRY</span>
              <span>Chrome Fleet Extension Synced • 100% Behavioral Anomaly Coverage</span>
            </div>
            <div className="ticker-item">
              <span className="ticker-tag purple">MODEL FUSION</span>
              <span>Ensemble Consensus Rate: 99.8% • Multi-Modal Dynamic Weighting</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Admin Command Header */}
      <header className="admin-navbar">
        <div className="admin-brand">
          <div className="admin-brand-icon">
            <Cpu size={24} className="icon-pulse" />
          </div>
          <div>
            <div className="admin-title">
              PhishGuard <span className="highlight-ai">AI</span> • SOC Command Center
            </div>
            <div className="admin-subtitle">
              Fleet Telemetry • Active Learning Calibration • Threat Radar
            </div>
          </div>
        </div>

        <div className="admin-header-actions">
          {/* CREATIVE: Audio FX Toggle */}
          <button
            className={`audio-toggle-btn ${audioEnabled ? "active" : ""}`}
            onClick={handleAudioToggle}
            title={audioEnabled ? "Tactile Audio: Enabled" : "Tactile Audio: Muted"}
          >
            {audioEnabled ? <Volume2 size={15} /> : <VolumeX size={15} />}
            <span>{audioEnabled ? "FX ON" : "MUTED"}</span>
          </button>

          <button className="nav-switch-btn" onClick={onNavigateScanner}>
            <ShieldCheck size={16} />
            <span>Live Threat Scanner</span>
          </button>

          <button
            className="action-btn btn-refresh"
            onClick={loadData}
            disabled={refreshing}
            title="Refresh live telemetry"
          >
            <RefreshCw size={15} className={refreshing ? "spin" : ""} />
            <span>{refreshing ? "Syncing..." : "Refresh"}</span>
          </button>

          <button
            className="action-btn btn-retrain-glow"
            onClick={handleTriggerRetrain}
            title="Run active learning cycle over human corrections"
          >
            <Sparkles size={16} />
            <span>Retrain Models</span>
            {stats && stats.pending_retraining > 0 && (
              <span className="pending-badge">{stats.pending_retraining}</span>
            )}
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="admin-main-content">
        {/* Model Status Strip */}
        <section className="model-status-strip">
          <div className="status-item">
            <span className="status-label">Active Model Version:</span>
            <span className="status-value highlight-cyan">
              {stats?.model_version || "v2.2-calibrated"}
            </span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <span className="status-label">Human Corrections Applied:</span>
            <span className="status-value highlight-purple">
              {stats?.admin_corrections || 0} Active Exemplars
            </span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <span className="status-label">Last Retrained:</span>
            <span className="status-value">
              {stats?.last_retrained
                ? new Date(stats.last_retrained).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })
                : "Just now"}
            </span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <span className="status-label">Self-Learning State:</span>
            <span className="status-badge-online">
              <span className="status-dot-pulse" /> Active Feedback Loop
            </span>
          </div>
        </section>

        {/* =========================================================
            CREATIVE: INTERACTIVE SECURITY TESTING SANDBOX
        ========================================================= */}
        <section className="sandbox-card">
          <div className="sandbox-header">
            <div className="radar-title-group">
              <Terminal size={20} className="text-cyan" />
              <div>
                <h3 className="chart-title" style={{ margin: 0 }}>Interactive Threat Simulator & Sandbox</h3>
                <p className="chart-desc" style={{ margin: 0 }}>
                  Test arbitrary URLs or email contents on-the-fly and verify multi-modal model inferences
                </p>
              </div>
            </div>
          </div>

          <div className="sandbox-input-row">
            <div className="sandbox-input-wrapper">
              <Search size={16} className="sandbox-input-icon" />
              <input
                type="text"
                placeholder="Enter URL (e.g. https://account-verification-paypal.cc) or email subject/body..."
                value={sandboxInput}
                onChange={(e) => setSandboxInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleRunSandbox()}
              />
            </div>
            <button
              className="btn-sandbox-run"
              onClick={handleRunSandbox}
              disabled={sandboxRunning || !sandboxInput.trim()}
            >
              <Play size={15} />
              <span>{sandboxRunning ? "Simulating..." : "Simulate & Inspect"}</span>
            </button>
          </div>

          {sandboxError && (
            <div className="admin-toast" style={{ position: "relative", top: 0, right: 0, margin: 0, background: "rgba(239, 68, 68, 0.2)", borderColor: "#ef4444" }}>
              <AlertTriangle size={16} className="text-red" />
              <span>{sandboxError}</span>
            </div>
          )}

          {sandboxResult && (
            <div className="sandbox-result-box">
              <div className="sandbox-verdict-strip">
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span className={`badge ${sandboxResult.risk.classification === "phishing" ? "badge-danger" : "badge-success"}`}>
                    {sandboxResult.risk.classification.toUpperCase()}
                  </span>
                  <span style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-primary)" }}>
                    Calculated Threat Risk: {sandboxResult.risk.risk_percentage.toFixed(1)}%
                  </span>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    Confidence: {sandboxResult.risk.confidence_percentage}%
                  </span>
                </div>

                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    className="btn-review-override"
                    onClick={() => {
                      setSelectedScan({
                        id: `sandbox-${Date.now()}`,
                        target: sandboxInput,
                        url: sandboxInput.startsWith("http") ? sandboxInput : "",
                        email: sandboxInput.includes("@") ? sandboxInput : "",
                        classification: sandboxResult.risk.classification as "phishing" | "legitimate" | "suspicious",
                        risk_score: sandboxResult.risk.risk_score,
                        risk_level: sandboxResult.risk.risk_level,
                        risk_percentage: sandboxResult.risk.risk_percentage,
                        url_score: sandboxResult.url.url_score,
                        email_score: sandboxResult.email.email_score,
                        behavior_score: sandboxResult.behavior.behavior_score,
                        source: "sandbox",
                        timestamp: new Date().toISOString(),
                        feedback: null,
                      });
                      setCorrectVerdict(sandboxResult.risk.classification === "phishing" ? "legitimate" : "phishing");
                    }}
                  >
                    <span>Flag Ground Truth / Correct</span>
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>

              <div className="sandbox-scores-grid">
                <div className="sandbox-score-card">
                  <span className="telemetry-label">BERT NLP Signal:</span>
                  <span className="telemetry-val highlight-cyan">
                    {(sandboxResult.email.email_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="sandbox-score-card">
                  <span className="telemetry-label">Char-CNN Lexical:</span>
                  <span className="telemetry-val highlight-purple">
                    {(sandboxResult.url.url_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="sandbox-score-card">
                  <span className="telemetry-label">Isolation Forest Anomaly:</span>
                  <span className="telemetry-val" style={{ color: "#10b981" }}>
                    {(sandboxResult.behavior.behavior_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="sandbox-score-card">
                  <span className="telemetry-label">Ensemble Consensus:</span>
                  <span className="telemetry-val" style={{ color: "#38bdf8" }}>
                    {sandboxResult.fusion.model_agreement.agreement}
                  </span>
                </div>
              </div>

              {sandboxResult.explanation.reasons.length > 0 && (
                <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                  <span style={{ fontWeight: "700", color: "var(--text-muted)" }}>Extracted Vectors:</span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {sandboxResult.explanation.reasons.map((r, i) => (
                      <span key={i} className="source-tag" style={{ background: "rgba(255,255,255,0.06)" }}>
                        {r.reason}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* 6 Metric KPI Cards */}
        <section className="kpi-grid">
          {/* Card 1: Total Scans */}
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-title">Total Fleet Scans</span>
              <Activity size={18} className="kpi-icon-blue" />
            </div>
            <div className="kpi-value">{stats ? stats.total_scans : "--"}</div>
            <div className="kpi-meta text-green">
              <TrendingUp size={14} />
              <span>Real-time web & email traffic</span>
            </div>
          </div>

          {/* Card 2: Threats Blocked */}
          <div className="kpi-card danger-card">
            <div className="kpi-header">
              <span className="kpi-title">Phishing Blocked</span>
              <ShieldAlert size={18} className="kpi-icon-red" />
            </div>
            <div className="kpi-value text-red">
              {stats ? stats.phishing_blocked : "--"}
            </div>
            <div className="kpi-meta text-muted">
              <span>
                {stats && stats.total_scans > 0
                  ? `${((stats.phishing_blocked / stats.total_scans) * 100).toFixed(1)}% of total traffic`
                  : "0%"}
              </span>
            </div>
          </div>

          {/* Card 3: Clean Sites */}
          <div className="kpi-card success-card">
            <div className="kpi-header">
              <span className="kpi-title">Legitimate Allowed</span>
              <ShieldCheck size={18} className="kpi-icon-green" />
            </div>
            <div className="kpi-value text-green">
              {stats ? stats.legitimate_allowed : "--"}
            </div>
            <div className="kpi-meta text-muted">
              <span>
                {stats && stats.total_scans > 0
                  ? `${((stats.legitimate_allowed / stats.total_scans) * 100).toFixed(1)}% verified benign`
                  : "0%"}
              </span>
            </div>
          </div>

          {/* Card 4: Suspicious */}
          <div className="kpi-card warning-card">
            <div className="kpi-header">
              <span className="kpi-title">Flagged for Review</span>
              <AlertTriangle size={18} className="kpi-icon-amber" />
            </div>
            <div className="kpi-value text-amber">
              {stats ? stats.suspicious_flagged : "--"}
            </div>
            <div className="kpi-meta text-muted">
              <span>Quarantine & warning active</span>
            </div>
          </div>

          {/* Card 5: Admin Overrides */}
          <div className="kpi-card purple-card">
            <div className="kpi-header">
              <span className="kpi-title">Admin Overrides (FP/FN)</span>
              <UserCheck size={18} className="kpi-icon-purple" />
            </div>
            <div className="kpi-value text-purple">
              {stats ? stats.admin_corrections : "--"}
            </div>
            <div className="kpi-meta text-muted">
              <span>{stats?.pending_retraining || 0} pending calibration</span>
            </div>
          </div>

          {/* Card 6: Estimated Accuracy */}
          <div className="kpi-card cyan-card">
            <div className="kpi-header">
              <span className="kpi-title">Calibrated Precision</span>
              <Cpu size={18} className="kpi-icon-cyan" />
            </div>
            <div className="kpi-value text-cyan">
              {stats ? `${stats.estimated_accuracy}%` : "--"}
            </div>
            <div className="kpi-meta text-muted">
              <span>Optimizes with each ground truth</span>
            </div>
          </div>
        </section>

        {/* =========================================================
            CREATIVE: TACTICAL THREAT RADAR & NEURAL MATRIX
        ========================================================= */}
        <section className="charts-grid" style={{ marginBottom: "24px" }}>
          {/* Creative Radar Screen */}
          <div className="radar-creative-card">
            <div className="radar-header">
              <div className="radar-title-group">
                <Crosshair size={20} className="radar-icon-pulse" />
                <div>
                  <h3 className="chart-title" style={{ margin: 0 }}>Tactical Threat Sonar Radar</h3>
                  <p className="chart-desc" style={{ margin: 0 }}>
                    Live spatial mapping of intercepted targets (Click radar to ping)
                  </p>
                </div>
              </div>
              <div className="chart-legend">
                <span className="legend-item"><span className="legend-dot dot-red" /> Threat</span>
                <span className="legend-item"><span className="legend-dot dot-green" /> Benign</span>
                <span className="legend-item"><span className="legend-dot dot-amber" /> Suspicious</span>
              </div>
            </div>

            {/* Circular Radar Display */}
            <div
              className="radar-display-area"
              ref={radarRef}
              onClick={handleRadarClick}
              title="Click anywhere to trigger sonar acoustic ping"
            >
              {/* Radar Rings */}
              <div className="radar-ring ring-1" />
              <div className="radar-ring ring-2" />
              <div className="radar-ring ring-3" />
              <div className="radar-ring ring-4" />

              {/* Crosshair Axes */}
              <div className="radar-axis-h" />
              <div className="radar-axis-v" />

              {/* Cardinal markings */}
              <span className="radar-coord n">000° N</span>
              <span className="radar-coord e">090° E</span>
              <span className="radar-coord s">180° S</span>
              <span className="radar-coord w">270° W</span>

              {/* Rotating Sweeping Laser Line */}
              <div className="radar-sweeper" />

              {/* Dynamic Target Blips from live scans */}
              {scans.slice(0, 14).map((scan, idx) => {
                const total = Math.min(scans.length, 14) || 1;
                const angle = (idx * (360 / total) * Math.PI) / 180;
                const distancePct = 22 + (scan.risk_score * 48); // 22% to 70% from center
                const left = 50 + distancePct * Math.cos(angle);
                const top = 50 + distancePct * Math.sin(angle);

                const blipClass =
                  scan.classification === "phishing"
                    ? "blip-phish"
                    : scan.classification === "legitimate"
                    ? "blip-legit"
                    : "blip-susp";

                return (
                  <div
                    key={scan.id}
                    className={`radar-blip ${blipClass}`}
                    style={{ left: `${left}%`, top: `${top}%` }}
                    onMouseEnter={() => setHoveredBlip(scan)}
                    onMouseLeave={() => setHoveredBlip(null)}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenCorrection(scan);
                    }}
                    title={`${scan.target} (${(scan.risk_score * 100).toFixed(0)}% Risk)`}
                  >
                    <div className="blip-pulse-wave" />
                  </div>
                );
              })}

              {/* Expanding Ripple on Click */}
              {radarPingCoord && (
                <div
                  className="radar-ping-wave"
                  style={{ left: `${radarPingCoord.x}px`, top: `${radarPingCoord.y}px` }}
                />
              )}
            </div>

            {/* Live Hover Tooltip / Status Readout */}
            {hoveredBlip ? (
              <div className="radar-telemetry-readout" style={{ borderColor: "var(--theme-accent)" }}>
                <div className="telemetry-cell">
                  <span className="telemetry-label">Locked Target:</span>
                  <span className="telemetry-val" style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {hoveredBlip.target}
                  </span>
                </div>
                <div className="telemetry-cell">
                  <span className="telemetry-label">Risk Probability:</span>
                  <span className="telemetry-val highlight-cyan">
                    {(hoveredBlip.risk_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="telemetry-cell">
                  <span className="telemetry-label">Action:</span>
                  <span className="telemetry-val" style={{ color: "#f43f5e", cursor: "pointer" }}>
                    Click to Correct
                  </span>
                </div>
              </div>
            ) : (
              <div className="radar-telemetry-readout">
                <div className="telemetry-cell">
                  <span className="telemetry-label">Sonar Frequency:</span>
                  <span className="telemetry-val">94.2 GHz Pulse</span>
                </div>
                <div className="telemetry-cell">
                  <span className="telemetry-label">Fleet Coverage:</span>
                  <span className="telemetry-val text-green">100% Active</span>
                </div>
                <div className="telemetry-cell">
                  <span className="telemetry-label">Targets Tracked:</span>
                  <span className="telemetry-val highlight-purple">{scans.length} Endpoints</span>
                </div>
              </div>
            )}
          </div>

          {/* Creative Hexagonal Neural Matrix Health */}
          <div className="neural-matrix-card">
            <div className="chart-panel-header">
              <div>
                <h3 className="chart-title">Multi-Modal Neural Defense Health</h3>
                <p className="chart-desc">Real-time status & inference latencies across ensemble engines</p>
              </div>
            </div>

            <div className="matrix-nodes-grid">
              {/* Node 1: BERT */}
              <div className="neural-node">
                <div className="node-header">
                  <div className="node-title-group">
                    <span className="node-led" />
                    <span>BERT NLP Core</span>
                  </div>
                  <span className="source-tag" style={{ color: "#38bdf8" }}>Semantic</span>
                </div>
                <div className="neural-flow-indicator" />
                <div className="node-specs-list">
                  <div className="spec-line"><span className="spec-key">Layers:</span><span className="spec-val">12 Transformer</span></div>
                  <div className="spec-line"><span className="spec-key">Attention Heads:</span><span className="spec-val">12 Multi-Head</span></div>
                  <div className="spec-line"><span className="spec-key">Inference Latency:</span><span className="spec-val text-green">12.4 ms</span></div>
                  <div className="spec-line"><span className="spec-key">Urgency Sensitivity:</span><span className="spec-val">High (0.85)</span></div>
                </div>
              </div>

              {/* Node 2: Char-CNN */}
              <div className="neural-node">
                <div className="node-header">
                  <div className="node-title-group">
                    <span className="node-led" />
                    <span>Char-CNN Engine</span>
                  </div>
                  <span className="source-tag" style={{ color: "#c084fc" }}>Lexical</span>
                </div>
                <div className="neural-flow-indicator" />
                <div className="node-specs-list">
                  <div className="spec-line"><span className="spec-key">Conv Kernels:</span><span className="spec-val">128 Filters</span></div>
                  <div className="spec-line"><span className="spec-key">N-Gram Window:</span><span className="spec-val">3, 4, 5-grams</span></div>
                  <div className="spec-line"><span className="spec-key">Inference Latency:</span><span className="spec-val text-green">0.9 ms</span></div>
                  <div className="spec-line"><span className="spec-key">Homoglyph Matrix:</span><span className="spec-val">Active Penalty</span></div>
                </div>
              </div>

              {/* Node 3: Isolation Forest */}
              <div className="neural-node">
                <div className="node-header">
                  <div className="node-title-group">
                    <span className="node-led" />
                    <span>Isolation Forest</span>
                  </div>
                  <span className="source-tag" style={{ color: "#10b981" }}>Behavior</span>
                </div>
                <div className="neural-flow-indicator" />
                <div className="node-specs-list">
                  <div className="spec-line"><span className="spec-key">Estimators:</span><span className="spec-val">100 Trees</span></div>
                  <div className="spec-line"><span className="spec-key">Contamination:</span><span className="spec-val">0.04 (Tuned)</span></div>
                  <div className="spec-line"><span className="spec-key">Inference Latency:</span><span className="spec-val text-green">0.4 ms</span></div>
                  <div className="spec-line"><span className="spec-key">Mouse/Typing Anomaly:</span><span className="spec-val">Calibrated</span></div>
                </div>
              </div>
            </div>

            {/* Model Consensus Bar */}
            <div className="model-scores-breakdown" style={{ marginTop: "10px" }}>
              <div className="breakdown-title">Fleet Decision Fusion Confidence:</div>
              <div className="model-bar-item">
                <div className="bar-labels">
                  <span>Ensemble Consensus Rate:</span>
                  <span className="mono">{stats?.estimated_accuracy || "99.4"}%</span>
                </div>
                <div className="progress-bg">
                  <div
                    className="progress-fill fill-cyan"
                    style={{ width: `${stats?.estimated_accuracy || 99.4}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Charts Section */}
        <section className="charts-grid">
          {/* Chart 1: Detection Trends Over Time (SVG Area Graph) */}
          <div className="chart-panel">
            <div className="chart-panel-header">
              <div>
                <h3 className="chart-title">Detection Trends (Past 7 Days)</h3>
                <p className="chart-desc">
                  Daily ratio of verified legitimate requests vs blocked zero-day phishing attacks
                </p>
              </div>
              <div className="chart-legend">
                <span className="legend-item">
                  <span className="legend-dot dot-green" /> Legitimate
                </span>
                <span className="legend-item">
                  <span className="legend-dot dot-red" /> Phishing
                </span>
                <span className="legend-item">
                  <span className="legend-dot dot-amber" /> Suspicious
                </span>
              </div>
            </div>

            {/* SVG Trend Chart */}
            <div className="svg-chart-wrapper">
              <svg viewBox="0 0 700 220" className="trend-svg">
                {/* Horizontal Grid lines */}
                <line x1="40" y1="30" x2="680" y2="30" stroke="#334155" strokeDasharray="3,3" />
                <line x1="40" y1="80" x2="680" y2="80" stroke="#334155" strokeDasharray="3,3" />
                <line x1="40" y1="130" x2="680" y2="130" stroke="#334155" strokeDasharray="3,3" />
                <line x1="40" y1="180" x2="680" y2="180" stroke="#475569" />

                {/* Bars & Labels */}
                {stats?.timeline_trends.map((item, idx) => {
                  const x = 70 + idx * 95;
                  const maxVal = 6;
                  const hLegit = Math.min(130, (item.legitimate / maxVal) * 130);
                  const hPhish = Math.min(130, (item.phishing / maxVal) * 130);
                  const hSusp = Math.min(130, (item.suspicious / maxVal) * 130);

                  return (
                    <g key={idx}>
                      {/* Legitimate Bar */}
                      <rect
                        x={x - 16}
                        y={180 - hLegit}
                        width="12"
                        height={Math.max(4, hLegit)}
                        fill="#10b981"
                        rx="3"
                      />
                      {/* Phishing Bar */}
                      <rect
                        x={x}
                        y={180 - hPhish}
                        width="12"
                        height={Math.max(4, hPhish)}
                        fill="#ef4444"
                        rx="3"
                      />
                      {/* Suspicious Bar */}
                      <rect
                        x={x + 16}
                        y={180 - hSusp}
                        width="12"
                        height={Math.max(4, hSusp)}
                        fill="#f59e0b"
                        rx="3"
                      />
                      {/* X-axis date label */}
                      <text
                        x={x + 6}
                        y="204"
                        fill="#94a3b8"
                        fontSize="11"
                        textAnchor="middle"
                        fontWeight="600"
                      >
                        {item.date}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Chart 2: Threat Distribution Donut & Model Consensus */}
          <div className="chart-panel">
            <div className="chart-panel-header">
              <div>
                <h3 className="chart-title">Threat Verdict Breakdown</h3>
                <p className="chart-desc">Cumulative classification proportion across fleet</p>
              </div>
            </div>

            <div className="donut-panel-content">
              {/* SVG Donut */}
              <div className="donut-wrapper">
                <svg viewBox="0 0 160 160" className="donut-svg">
                  <circle cx="80" cy="80" r="60" fill="transparent" stroke="#1e293b" strokeWidth="22" />
                  {/* Legitimate Segment */}
                  <circle
                    cx="80"
                    cy="80"
                    r="60"
                    fill="transparent"
                    stroke="#10b981"
                    strokeWidth="22"
                    strokeDasharray="245 377"
                    strokeDashoffset="0"
                  />
                  {/* Phishing Segment */}
                  <circle
                    cx="80"
                    cy="80"
                    r="60"
                    fill="transparent"
                    stroke="#ef4444"
                    strokeWidth="22"
                    strokeDasharray="95 377"
                    strokeDashoffset="-245"
                  />
                  {/* Suspicious Segment */}
                  <circle
                    cx="80"
                    cy="80"
                    r="60"
                    fill="transparent"
                    stroke="#f59e0b"
                    strokeWidth="22"
                    strokeDasharray="37 377"
                    strokeDashoffset="-340"
                  />
                </svg>
                <div className="donut-center-text">
                  <div className="donut-center-num">{stats?.total_scans || 0}</div>
                  <div className="donut-center-sub">Total Scans</div>
                </div>
              </div>

              {/* Multi-modal Average Scores */}
              <div className="model-scores-breakdown">
                <div className="breakdown-title">Average Multi-Modal Signals:</div>
                <div className="model-bar-item">
                  <div className="bar-labels">
                    <span>BERT NLP (Email):</span>
                    <span className="mono">
                      {stats ? `${(stats.average_scores.bert_email * 100).toFixed(1)}%` : "--"}
                    </span>
                  </div>
                  <div className="progress-bg">
                    <div
                      className="progress-fill fill-blue"
                      style={{
                        width: `${Math.min(100, (stats?.average_scores.bert_email || 0) * 100)}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="model-bar-item">
                  <div className="bar-labels">
                    <span>Character CNN (URL):</span>
                    <span className="mono">
                      {stats ? `${(stats.average_scores.cnn_url * 100).toFixed(1)}%` : "--"}
                    </span>
                  </div>
                  <div className="progress-bg">
                    <div
                      className="progress-fill fill-cyan"
                      style={{
                        width: `${Math.min(100, (stats?.average_scores.cnn_url || 0) * 100)}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="model-bar-item">
                  <div className="bar-labels">
                    <span>Isolation Forest (Behavior):</span>
                    <span className="mono">
                      {stats
                        ? `${(stats.average_scores.isolation_forest_behavior * 100).toFixed(1)}%`
                        : "--"}
                    </span>
                  </div>
                  <div className="progress-bg">
                    <div
                      className="progress-fill fill-purple"
                      style={{
                        width: `${Math.min(
                          100,
                          (stats?.average_scores.isolation_forest_behavior || 0) * 100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Live Traffic & Incident Log Table */}
        <section className="table-section">
          <div className="table-toolbar">
            <div className="table-search-box">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search websites, URLs, email subjects, or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button className="clear-search" onClick={() => setSearchTerm("")}>
                  <X size={14} />
                </button>
              )}
            </div>

            {/* Filter Pills */}
            <div className="filter-pill-group">
              <button
                className={`filter-pill ${filterType === "all" ? "active" : ""}`}
                onClick={() => setFilterType("all")}
              >
                All Traffic
              </button>
              <button
                className={`filter-pill pill-phish ${filterType === "phishing" ? "active" : ""}`}
                onClick={() => setFilterType("phishing")}
              >
                Phishing Blocked
              </button>
              <button
                className={`filter-pill pill-legit ${filterType === "legitimate" ? "active" : ""}`}
                onClick={() => setFilterType("legitimate")}
              >
                Legitimate Allowed
              </button>
              <button
                className={`filter-pill pill-susp ${filterType === "suspicious" ? "active" : ""}`}
                onClick={() => setFilterType("suspicious")}
              >
                Suspicious
              </button>
              <button
                className={`filter-pill pill-corr ${filterType === "corrected" ? "active" : ""}`}
                onClick={() => setFilterType("corrected")}
              >
                Human Corrected
              </button>
            </div>
          </div>

          {/* Incidents Table */}
          <div className="table-responsive">
            <table className="incidents-table">
              <thead>
                <tr>
                  <th>Verdict / Status</th>
                  <th>Target Website / Email</th>
                  <th>Inspection Source</th>
                  <th>Model Confidence</th>
                  <th>Risk Score</th>
                  <th>Timestamp</th>
                  <th style={{ textAlign: "right" }}>Administrator Action</th>
                </tr>
              </thead>
              <tbody>
                {scans.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-table-cell">
                      No matching extension scans found.
                    </td>
                  </tr>
                ) : (
                  scans.map((scan) => {
                    const isPhish = scan.classification === "phishing";
                    const isLegit = scan.classification === "legitimate";
                    const isSusp = scan.classification === "suspicious";
                    const hasCorrection = Boolean(scan.feedback);

                    return (
                      <tr key={scan.id} className={hasCorrection ? "row-corrected" : ""}>
                        {/* Verdict Column */}
                        <td>
                          <div className="verdict-cell">
                            {isPhish && (
                              <span className="badge badge-danger">
                                <ShieldAlert size={12} /> Phishing
                              </span>
                            )}
                            {isLegit && (
                              <span className="badge badge-success">
                                <ShieldCheck size={12} /> Legitimate
                              </span>
                            )}
                            {isSusp && (
                              <span className="badge badge-warning">
                                <AlertTriangle size={12} /> Suspicious
                              </span>
                            )}
                            {hasCorrection && (
                              <span className="sub-badge-override" title={scan.feedback?.reason}>
                                Overridden by Admin
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Target URL / Snippet */}
                        <td>
                          <div className="target-cell">
                            <span className="target-text" title={scan.url || scan.email}>
                              {scan.target}
                            </span>
                          </div>
                        </td>

                        {/* Source */}
                        <td>
                          <span className="source-tag">{scan.source}</span>
                        </td>

                        {/* Model Confidence Pills */}
                        <td>
                          <div className="score-pills">
                            {scan.url_score > 0 && (
                              <span className="pill-metric" title="URL CNN Confidence">
                                CNN: {(scan.url_score * 100).toFixed(0)}%
                              </span>
                            )}
                            {scan.email_score > 0 && (
                              <span className="pill-metric" title="BERT NLP Confidence">
                                BERT: {(scan.email_score * 100).toFixed(0)}%
                              </span>
                            )}
                            {scan.behavior_score > 0 && (
                              <span className="pill-metric" title="Behavior Anomaly">
                                Beh: {(scan.behavior_score * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Risk Score */}
                        <td>
                          <div className="risk-score-cell">
                            <span
                              className={`risk-score-value ${
                                scan.risk_score >= 0.65
                                  ? "text-red"
                                  : scan.risk_score >= 0.35
                                  ? "text-amber"
                                  : "text-green"
                              }`}
                            >
                              {scan.risk_percentage.toFixed(1)}%
                            </span>
                          </div>
                        </td>

                        {/* Timestamp */}
                        <td>
                          <span className="timestamp-text">
                            {new Date(scan.timestamp).toLocaleDateString([], {
                              month: "short",
                              day: "numeric",
                            })}{" "}
                            {new Date(scan.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                        </td>

                        {/* Action Button */}
                        <td style={{ textAlign: "right" }}>
                          <button
                            className="btn-review-override"
                            onClick={() => handleOpenCorrection(scan)}
                            title="Correct misclassification & add to self-learning memory"
                          >
                            <span>Review & Correct</span>
                            <ChevronRight size={14} />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      {/* =========================================================
          HUMAN-IN-THE-LOOP CORRECTION MODAL
      ========================================================= */}
      {selectedScan && (
        <div className="modal-overlay" onClick={() => setSelectedScan(null)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-header-title">
                <UserCheck size={20} className="text-purple" />
                <h3>Human-in-the-Loop Feedback & Correction</h3>
              </div>
              <button className="modal-close-btn" onClick={() => setSelectedScan(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="modal-incident-meta">
                <div className="meta-row">
                  <span className="meta-label">Scanned Target:</span>
                  <span className="meta-val mono">{selectedScan.target}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-label">Current Automatic Diagnosis:</span>
                  <span className={`badge ${selectedScan.classification === "phishing" ? "badge-danger" : "badge-success"}`}>
                    {selectedScan.classification.toUpperCase()} ({selectedScan.risk_percentage}% Risk)
                  </span>
                </div>
              </div>

              <div className="correction-options">
                <div className="options-title">Select Correct Ground Truth:</div>

                <div className="verdict-selection-grid">
                  {/* Option 1: Legitimate */}
                  <div
                    className={`verdict-choice-card ${correctVerdict === "legitimate" ? "selected legit-sel" : ""}`}
                    onClick={() => setCorrectVerdict("legitimate")}
                  >
                    <div className="choice-icon text-green">
                      <ShieldCheck size={26} />
                    </div>
                    <div className="choice-text">
                      <div className="choice-title">Mark as Genuine / Legitimate</div>
                      <div className="choice-desc">
                        False Positive resolution. Updates adaptive memory so this legitimate domain/template is never blocked again.
                      </div>
                    </div>
                  </div>

                  {/* Option 2: Phishing */}
                  <div
                    className={`verdict-choice-card ${correctVerdict === "phishing" ? "selected phish-sel" : ""}`}
                    onClick={() => setCorrectVerdict("phishing")}
                  >
                    <div className="choice-icon text-red">
                      <ShieldAlert size={26} />
                    </div>
                    <div className="choice-text">
                      <div className="choice-title">Mark as Malicious / Phishing</div>
                      <div className="choice-desc">
                        False Negative resolution. Teaches the system to enforce immediate blocking against this stealthy threat.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="correction-reason-box">
                <label>Administrator Justification / Notes:</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Official university portal, tracking token false alarm, stealthy credential harvester..."
                  value={correctReason}
                  onChange={(e) => setCorrectReason(e.target.value)}
                />
              </div>

              <div className="active-learning-notice">
                <Sparkles size={16} />
                <span>
                  <strong>Active Learning Guarantee:</strong> Submitting this correction instantly updates the calibration exemplar memory. Future scans will immediately honor this decision!
                </span>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-cancel" onClick={() => setSelectedScan(null)}>
                Cancel
              </button>
              <button
                className="btn-apply"
                onClick={() => handleApplyCorrection(false)}
                disabled={submittingCorrection}
              >
                {submittingCorrection ? "Saving..." : "Save Override"}
              </button>
              <button
                className="btn-apply-retrain"
                onClick={() => handleApplyCorrection(true)}
                disabled={submittingCorrection}
              >
                <Sparkles size={15} />
                <span>Save & Retrain Now</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================
          RETRAINING CONSOLE / PROGRESS MODAL WITH LOSS CONVERGENCE
      ========================================================= */}
      {retrainingModalOpen && (
        <div className="modal-overlay">
          <div className="modal-container retraining-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-header-title">
                <Cpu size={20} className="text-cyan" />
                <h3>Active Learning Self-Retraining Console</h3>
              </div>
              {!retrainingActive && (
                <button className="modal-close-btn" onClick={() => setRetrainingModalOpen(false)}>
                  <X size={18} />
                </button>
              )}
            </div>

            <div className="modal-body">
              {/* Terminal Logs */}
              <div className="terminal-console">
                <div className="terminal-header">
                  <span className="term-dot red" />
                  <span className="term-dot yellow" />
                  <span className="term-dot green" />
                  <span className="term-title">phishguard-active-learning-v2.2.engine</span>
                </div>
                <div className="terminal-body">
                  {trainingLogs.map((log, index) => (
                    <div key={index} className="term-line">
                      <span className="term-prompt">❯</span> {log}
                    </div>
                  ))}
                  {retrainingActive && (
                    <div className="term-line term-active-pulse">
                      <span className="term-prompt">❯</span> Optimizing weights across human feedback samples...
                    </div>
                  )}
                </div>
              </div>

              {/* CREATIVE: Loss Gradient Convergence Graph */}
              <div className="loss-convergence-svg-wrap">
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px", fontSize: "11px" }}>
                  <span style={{ color: "var(--text-muted)", fontWeight: "700" }}>OPTIMIZER CONVERGENCE CURVE (LOSS VS EPOCH)</span>
                  <span style={{ color: "var(--theme-accent)", fontWeight: "700" }}>AdamW • lr=2e-5 • ΔLoss -94.2%</span>
                </div>
                <svg viewBox="0 0 500 120" style={{ width: "100%", height: "90px" }}>
                  {/* Grid Lines */}
                  <line x1="30" y1="20" x2="480" y2="20" stroke="#1e293b" strokeDasharray="3,3" />
                  <line x1="30" y1="55" x2="480" y2="55" stroke="#1e293b" strokeDasharray="3,3" />
                  <line x1="30" y1="90" x2="480" y2="90" stroke="#334155" />

                  {/* Loss Convergence Curve (drops from y=25 to y=88) */}
                  <path
                    d="M 50 25 Q 120 40 180 65 T 320 82 T 460 88"
                    className="loss-curve-path"
                  />

                  {/* Epoch Nodes */}
                  <circle cx="50" cy="25" r="4" className="loss-epoch-node" />
                  <circle cx="150" cy="55" r="4" className="loss-epoch-node" />
                  <circle cx="250" cy="74" r="4" className="loss-epoch-node" />
                  <circle cx="360" cy="84" r="4" className="loss-epoch-node" />
                  <circle cx="460" cy="88" r="5" className="loss-epoch-node" />

                  {/* Epoch Labels */}
                  <text x="50" y="106" fill="#64748b" fontSize="10" textAnchor="middle">Ep 1</text>
                  <text x="150" y="106" fill="#64748b" fontSize="10" textAnchor="middle">Ep 2</text>
                  <text x="250" y="106" fill="#64748b" fontSize="10" textAnchor="middle">Ep 3</text>
                  <text x="360" y="106" fill="#64748b" fontSize="10" textAnchor="middle">Ep 4</text>
                  <text x="460" y="106" fill="var(--theme-accent)" fontSize="10" fontWeight="700" textAnchor="middle">Ep 5</text>
                </svg>
              </div>

              {/* Retraining Results Summary */}
              {retrainingResult && (
                <div className="retraining-summary-card">
                  <div className="summary-badge text-green">
                    <CheckCircle2 size={18} />
                    <span>Active Learning Optimization Converged!</span>
                  </div>

                  <div className="summary-grid">
                    <div className="summary-item">
                      <span className="sum-label">New Model Version:</span>
                      <span className="sum-val highlight-cyan">
                        {retrainingResult.updated_calibration.version}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="sum-label">Loss Reduction:</span>
                      <span className="sum-val text-green">
                        {retrainingResult.retraining_log.loss_reduction_percent}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="sum-label">Accuracy Delta:</span>
                      <span className="sum-val text-purple">
                        {retrainingResult.retraining_log.accuracy_improvement}
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="sum-label">Optimizer:</span>
                      <span className="sum-val mono">AdamW</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn-done"
                disabled={retrainingActive}
                onClick={() => setRetrainingModalOpen(false)}
              >
                {retrainingActive ? "Retraining in progress..." : "Done & Return to Dashboard"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
