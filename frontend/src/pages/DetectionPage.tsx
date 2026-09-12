import { useEffect, useRef, useState } from "react";
import {
  ShieldCheck,
  Search,
  Activity,
} from "lucide-react";

import {
  analyzePhishing,
  type BehaviorData,
  type DetectionResult,
  ApiError,
} from "../services/api";

import BehaviorTracker from "../utils/BehaviorTracker";


export default function DetectionPage() {
  const [email, setEmail] = useState("");
  const [url, setUrl] = useState("");

  const [behavior, setBehavior] =
    useState<BehaviorData>({
      num_clicks: 0,
      time_on_page: 0,
      num_redirects: 0,
      failed_logins: 0,
      mouse_speed: 0,
      typing_speed: 0,
      tab_switches: 0,
    });

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [result, setResult] =
    useState<DetectionResult | null>(null);

  const trackerRef =
    useRef<BehaviorTracker | null>(null);


  // ==========================================================
  // START BEHAVIOR TRACKING
  // ==========================================================

  useEffect(() => {
    const tracker =
      new BehaviorTracker();

    trackerRef.current =
      tracker;

    const interval =
      setInterval(() => {
        setBehavior(
          tracker.getBehavior()
        );
      }, 1000);

    return () => {
      clearInterval(interval);

      tracker.destroy();

      trackerRef.current = null;
    };
  }, []);


  // ==========================================================
  // ANALYZE
  // ==========================================================

  const handleAnalyze = async () => {
    setError("");
    setResult(null);

    if (!email.trim()) {
      setError(
        "Please enter email content."
      );
      return;
    }

    if (!url.trim()) {
      setError(
        "Please enter a URL."
      );
      return;
    }

    try {
      setLoading(true);

      const currentBehavior =
        trackerRef.current
          ? trackerRef.current.getBehavior()
          : behavior;

      const response =
        await analyzePhishing({
          email,
          url,
          behavior: currentBehavior,
        });

      if (response.result) {
        setResult(response.result);
      }
    } catch (err: unknown) {
      console.error(err);

      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to connect to the phishing detection server.");
      }
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="detection-page">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="page-header">

        <div className="header-icon">
          <ShieldCheck size={28} />
        </div>

        <div>
          <h1>
            PhishGuard AI
          </h1>

          <p>
            Multi-Modal Threat & Phishing Intelligence Platform (BERT + CNN + Isolation Forest)
          </p>
        </div>

      </header>


      {/* ======================================================
          INPUT CARD
      ====================================================== */}

      <section className="input-card">

        <div className="section-title">

          <h2>
            Detection Input
          </h2>

          <p>
            Provide the email and URL to analyze.
            Behavioral signals are collected automatically.
          </p>

        </div>


        {/* EMAIL */}

        <div className="input-group">

          <label>
            Email Content
          </label>

          <textarea
            value={email}
            onChange={(event) =>
              setEmail(
                event.target.value
              )
            }
            placeholder="Paste the email content here..."
            rows={10}
          />

        </div>


        {/* URL */}

        <div className="input-group">

          <label>
            URL
          </label>

          <input
            type="text"
            value={url}
            onChange={(event) =>
              setUrl(
                event.target.value
              )
            }
            placeholder="https://example.com"
          />

        </div>


        {/* ====================================================
            LIVE BEHAVIOR
        ==================================================== */}

        <div className="behavior-section">

          <div className="section-title">

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >

              <Activity
                size={19}
              />

              <h2>
                Behavioral Monitoring
              </h2>

            </div>

            <p>
              Behavioral signals are being
              collected automatically.
            </p>

          </div>


          <div className="behavior-grid">

            <BehaviorDisplay
              label="Clicks"
              value={
                behavior.num_clicks
              }
            />

            <BehaviorDisplay
              label="Time on Page"
              value={
                `${behavior.time_on_page}s`
              }
            />

            <BehaviorDisplay
              label="Mouse Speed"
              value={
                behavior.mouse_speed
              }
            />

            <BehaviorDisplay
              label="Typing Speed"
              value={
                behavior.typing_speed
              }
            />

            <BehaviorDisplay
              label="Tab Switches"
              value={
                behavior.tab_switches
              }
            />

            <BehaviorDisplay
              label="Redirects"
              value={
                behavior.num_redirects
              }
            />

            <BehaviorDisplay
              label="Failed Logins"
              value={
                behavior.failed_logins
              }
            />

          </div>

        </div>


        {/* ====================================================
            ERROR
        ==================================================== */}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}


        {/* ====================================================
            ANALYZE BUTTON
        ==================================================== */}

        <button
          className="analyze-button"
          onClick={
            handleAnalyze
          }
          disabled={loading}
        >

          <Search size={20} />

          {loading
            ? "Analyzing..."
            : "Analyze for Phishing"}

        </button>

      </section>


      {/* ======================================================
          RESULTS
      ====================================================== */}

      {result && (
        <ResultSection
          result={result}
        />
      )}

    </div>
  );
}


/* ============================================================
   BEHAVIOR DISPLAY
   ============================================================ */

function BehaviorDisplay({
  label,
  value,
}: {
  label: string;
  value: number | string;
}) {
  return (
    <div className="behavior-input">

      <label>
        {label}
      </label>

      <div
        style={{
          padding: "11px 12px",
          background: "#071321",
          border: "1px solid #243a55",
          borderRadius: "10px",
          color: "#e2e8f0",
          minHeight: "43px",
          display: "flex",
          alignItems: "center",
        }}
      >
        {value}
      </div>

    </div>
  );
}


/* ============================================================
   RESULT SECTION
   ============================================================ */

function ResultSection({
  result,
}: {
  result: DetectionResult;
}) {
  const risk =
    result.risk;

  const fusion =
    result.fusion;

  const explanation =
    result.explanation;

  return (
    <section className="result-section">

      {/* ====================================================
          RISK
      ==================================================== */}

      <div className="risk-card">

        <div>

          <p className="result-label">
            FINAL RISK SCORE
          </p>

          <h2>
            {risk.risk_percentage}%
          </h2>

        </div>


        <div className="risk-status">

          <strong>
            {risk.risk_level.toUpperCase()}
          </strong>

          <span>
            {risk.classification.toUpperCase()}
          </span>

        </div>

      </div>


      {/* ====================================================
          MODELS
      ==================================================== */}

      <div className="model-grid">

        <ModelCard
          name="BERT"
          score={
            result.email.email_score
          }
        />

        <ModelCard
          name="CNN"
          score={
            result.url.url_score
          }
        />

        <ModelCard
          name="Isolation Forest"
          score={
            result.behavior
              .behavior_score
          }
        />

      </div>


      {/* ====================================================
          INFORMATION
      ==================================================== */}

      <div className="info-grid">

        <div className="info-card">

          <h3>
            Fusion
          </h3>

          <p>
            Fused Score
          </p>

          <strong>
            {(
              fusion.fused_score *
              100
            ).toFixed(2)}
            %
          </strong>

          <p>
            Agreement:{" "}
            {
              fusion
                .model_agreement
                .agreement
            }
          </p>

        </div>


        <div className="info-card">

          <h3>
            Confidence
          </h3>

          <strong>
            {
              risk.confidence_percentage
            }%
          </strong>

          <p>
            Model confidence
          </p>

        </div>


        <div className="info-card">

          <h3>
            Recommended Action
          </h3>

          <strong>
            {
              risk.recommended_action
            }
          </strong>

        </div>

      </div>


      {/* ====================================================
          EXPLANATION
      ==================================================== */}

      <div className="explanation-card">

        <h2>
          Why was this detected?
        </h2>

        <p className="summary">
          {
            explanation.summary
          }
        </p>


        <div className="reason-list">

          {
            explanation.reasons.map(
              (
                reason,
                index: number
              ) => (

                <div
                  className={`reason reason-${reason.severity}`}
                  key={index}
                >

                  <div className="reason-header">

                    <strong>
                      {
                        reason.source
                          .toUpperCase()
                      }
                    </strong>

                    <span>
                      {
                        reason.severity
                          .toUpperCase()
                      }
                    </span>

                  </div>

                  <p>
                    {
                      reason.reason
                    }
                  </p>

                </div>

              )
            )
          }

        </div>

      </div>

    </section>
  );
}


/* ============================================================
   MODEL CARD
   ============================================================ */

function ModelCard({
  name,
  score,
}: {
  name: string;
  score: number;
}) {
  return (
    <div className="model-card">

      <p>
        {name}
      </p>

      <strong>
        {
          (
            score * 100
          ).toFixed(2)
        }%
      </strong>

      <div className="score-bar">

        <div
          className="score-fill"
          style={{
            width: `${
              score * 100
            }%`,
          }}
        />

      </div>

    </div>
  );
}