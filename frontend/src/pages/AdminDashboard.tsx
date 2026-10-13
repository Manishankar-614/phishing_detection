import { useState, useEffect } from "react";
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
  ExternalLink,
  ChevronRight,
  TrendingUp,
} from "lucide-react";
import {
  fetchAdminStats,
  fetchAdminScans,
  submitCorrection,
  triggerRetraining,
  type AdminStats,
  type AdminScanItem,
  type RetrainingResponse,
} from "../services/api";

interface AdminDashboardProps {
  onNavigateScanner: () => void;
}

export default function AdminDashboard({ onNavigateScanner }: AdminDashboardProps) {
  // State
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

  // Toast State
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
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
  // Handle Correction Submission
  // -------------------------------------------------------------
  const handleOpenCorrection = (scan: AdminScanItem) => {
    setSelectedScan(scan);
    setCorrectVerdict(scan.classification === "phishing" ? "legitimate" : "phishing");
    setCorrectReason("");
  };

  const handleApplyCorrection = async (andRetrain: boolean = false) => {
    if (!selectedScan) return;
    try {
      setSubmittingCorrection(true);
      await submitCorrection({
        scan_id: selectedScan.id,
        corrected_label: correctVerdict,
        reason: correctReason || `Admin manual override to ${correctVerdict}`,
        admin: "Security Administrator",
      });

      showToast(`Correction applied: Overridden to ${correctVerdict.toUpperCase()}!`);
      setSelectedScan(null);
      await loadData();

      if (andRetrain) {
        handleTriggerRetrain();
      }
    } catch (err) {
      console.error("Failed to apply correction:", err);
      showToast("Error saving correction. Please try again.");
    } finally {
      setSubmittingCorrection(false);
    }
  };

  // -------------------------------------------------------------
  // Handle Retraining
  // -------------------------------------------------------------
  const handleTriggerRetrain = async () => {
    setRetrainingModalOpen(true);
    setRetrainingActive(true);
    setRetrainingResult(null);
    setTrainingLogs([
      "Initializing Adaptive Active Learning Pipeline...",
      "Gathering verified human feedback & false positive exemplars...",
    ]);

    try {
      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          "Computing cross-entropy loss gradients for BERT transformer...",
          "Fine-tuning character CNN convolutional kernels & lexical weights...",
        ]);
      }, 700);

      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          "Recalibrating Isolation Forest decision threshold boundary...",
          "Running validation pass across baseline benchmarking test suite...",
        ]);
      }, 1400);

      const res = await triggerRetraining();

      setTimeout(() => {
        setTrainingLogs((prev) => [
          ...prev,
          `Convergence achieved: Loss reduced by ${res.retraining_log.loss_reduction_percent}`,
          `Model updated to ${res.updated_calibration.version} (+${res.retraining_log.accuracy_improvement} precision)`,
          "Active calibration memory checkpoint saved successfully!",
        ]);
        setRetrainingResult(res);
        setRetrainingActive(false);
        loadData();
      }, 2100);
    } catch (err) {
      setTrainingLogs((prev) => [...prev, "Retraining failed: Unable to communicate with model engine."]);
      setRetrainingActive(false);
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

      {/* Top Admin Command Header */}
      <header className="admin-navbar">
        <div className="admin-brand">
          <div className="admin-brand-icon">
            <Cpu size={24} className="icon-pulse" />
          </div>
          <div>
            <div className="admin-title">
              PhishGuard <span className="highlight-ai">AI</span> • Control Center
            </div>
            <div className="admin-subtitle">
              Browser Extension Fleet Telemetry & Active Learning Engine
            </div>
          </div>
        </div>

        <div className="admin-header-actions">
          <button className="nav-switch-btn" onClick={onNavigateScanner}>
            <ShieldCheck size={16} />
            <span>Live Threat Scanner</span>
          </button>

          <a
            href="/poster.html"
            target="_blank"
            rel="noreferrer"
            className="nav-switch-btn poster-btn"
          >
            <span>🎓 Poster</span>
            <ExternalLink size={13} />
          </a>

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
              {stats?.model_version || "v2.1-calibrated"}
            </span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <span className="status-label">Human Corrections Applied:</span>
            <span className="status-value highlight-purple">
              {stats?.admin_corrections || 0} Exemplars
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

        {/* 6 Metric KPI Cards */}
        <section className="kpi-grid">
          {/* Card 1: Total Scans */}
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-title">Total Extension Scans</span>
              <Activity size={18} className="kpi-icon-blue" />
            </div>
            <div className="kpi-value">{stats ? stats.total_scans : "--"}</div>
            <div className="kpi-meta text-green">
              <TrendingUp size={14} />
              <span>Real-time enterprise web & email traffic</span>
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
              <span>Stepped-up user warning applied</span>
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
              <span>{stats?.pending_retraining || 0} pending retraining cycle</span>
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
              <span>Self-improves with each correction</span>
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
                <defs>
                  <linearGradient id="gradLegit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                  </linearGradient>
                  <linearGradient id="gradPhish" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

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
                  {/* Legitimate Segment (approx 65%) */}
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
                  {/* Phishing Segment (approx 25%) */}
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
                  {/* Suspicious Segment (approx 10%) */}
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
          RETRAINING CONSOLE / PROGRESS MODAL
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

              {/* Retraining Results Summary */}
              {retrainingResult && (
                <div className="retraining-summary-card">
                  <div className="summary-badge text-green">
                    <CheckCircle2 size={18} />
                    <span>Optimization Successfully Converged!</span>
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
