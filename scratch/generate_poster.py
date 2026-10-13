import base64
import os

logo_path = r'c:\Docs\Phishing_Detection\poster\assets\gat_logo.png'
with open(logo_path, 'rb') as f:
    logo_b64 = base64.b64encode(f.read()).decode('utf-8')

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Project Poster - Adaptive Multi-Modal Phishing Detection | Global Academy of Technology</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Outfit:wght@500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-color: #e9eff6;
      --header-bg: #092240;
      --card-bg: #ffffff;
      --card-border: #d0e0f0;
      --primary-navy: #092240;
      --accent-blue: #1565c0;
      --accent-cyan: #0288d1;
      --text-dark: #1e293b;
      --text-muted: #475569;
      --team-bg: #dbe9f6;
      --tag-green: #2e7d32;
      --border-radius: 8px;
      --box-shadow: 0 4px 14px rgba(15, 34, 64, 0.08);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #1e293b;
      color: var(--text-dark);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 20px 10px 40px;
      overflow-x: auto;
    }}

    /* Top Control Bar */
    .top-toolbar {{
      width: 100%;
      max-width: 1440px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0f172a;
      color: #fff;
      padding: 12px 24px;
      border-radius: 10px;
      margin-bottom: 16px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.12);
      z-index: 100;
    }}

    .toolbar-title {{
      font-size: 15px;
      font-weight: 700;
      color: #60a5fa;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .toolbar-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: #2563eb;
      color: white;
      border: none;
      padding: 9px 18px;
      border-radius: 6px;
      font-size: 13.5px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s ease;
    }}
    .btn:hover {{
      background: #1d4ed8;
      transform: translateY(-1px);
    }}
    .btn-secondary {{
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.2);
    }}
    .btn-secondary:hover {{
      background: rgba(255,255,255,0.22);
    }}
    .btn-green {{
      background: #16a34a;
    }}
    .btn-green:hover {{
      background: #15803d;
    }}

    /* Poster Container (16:9 Standard Presentation / Poster Ratio) */
    .poster-viewport {{
      width: 1440px;
      height: 810px; /* Exact 16:9 ratio (1440 * 9 / 16) */
      background-color: var(--bg-color);
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      padding: 0;
      overflow: hidden;
      position: relative;
    }}

    /* College Header */
    .poster-header {{
      background: var(--header-bg);
      color: white;
      height: 96px;
      display: flex;
      align-items: center;
      padding: 0 26px;
      position: relative;
      border-bottom: 3.5px solid #1565c0;
    }}

    .logo-box {{
      background: #ffffff;
      padding: 4px 10px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 72px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }}

    .logo-box img {{
      height: 62px;
      width: auto;
      object-fit: contain;
    }}

    .header-text-container {{
      flex: 1;
      text-align: center;
      margin-right: 120px; /* balance out the logo on left */
    }}

    .college-name {{
      font-family: 'Outfit', sans-serif;
      font-size: 32px;
      font-weight: 900;
      letter-spacing: 2.2px;
      text-transform: uppercase;
      color: #ffffff;
      line-height: 1.15;
    }}

    .dept-name {{
      font-size: 19.5px;
      font-weight: 600;
      color: #90caf9;
      letter-spacing: 0.5px;
      margin-top: 2px;
    }}

    /* Main Poster Canvas */
    .poster-body {{
      flex: 1;
      padding: 12px 20px 12px 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    /* Title Card */
    .title-card {{
      background: var(--card-bg);
      border-radius: var(--border-radius);
      border: 1px solid var(--card-border);
      padding: 8px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: var(--box-shadow);
      min-height: 50px;
    }}

    .title-left {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .title-label {{
      font-family: 'Outfit', sans-serif;
      font-size: 15.5px;
      font-weight: 900;
      color: var(--primary-navy);
      letter-spacing: 0.5px;
      white-space: nowrap;
    }}

    .title-text {{
      font-family: 'Outfit', sans-serif;
      font-size: 16.5px;
      font-weight: 800;
      color: var(--accent-blue);
      letter-spacing: 0.2px;
    }}

    .title-sdg {{
      display: flex;
      align-items: center;
      gap: 7px;
      background: #e8f5e9;
      border: 1.2px solid #a5d6a7;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      color: var(--tag-green);
      white-space: nowrap;
    }}

    /* Team Banner */
    .team-card {{
      background: var(--team-bg);
      border-radius: var(--border-radius);
      border: 1px solid #c4daf0;
      padding: 6px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 13.5px;
      color: var(--primary-navy);
      font-weight: 600;
    }}

    .team-members {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .team-members span.tag {{
      font-weight: 800;
      color: #0d47a1;
      letter-spacing: 0.5px;
    }}

    .team-guide {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .team-guide span.guide-tag {{
      font-weight: 800;
      color: #0d47a1;
    }}

    /* 6-Card Grid Layout */
    .grid-container {{
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1.08fr 0.92fr;
      grid-template-rows: 1fr 1.34fr;
      gap: 11px;
    }}

    /* Content Cards */
    .card {{
      background: var(--card-bg);
      border-radius: var(--border-radius);
      border: 1px solid var(--card-border);
      box-shadow: var(--box-shadow);
      padding: 10px 15px;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
    }}

    /* Royal Blue Left Accent Indicator (Exact match to template!) */
    .card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 5.5px;
      height: 100%;
      background: #1565c0;
      border-radius: 8px 0 0 8px;
    }}

    .card-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 14.5px;
      font-weight: 900;
      color: var(--primary-navy);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 7px;
      display: flex;
      align-items: center;
      gap: 6px;
      border-bottom: 1.5px solid #e2edf8;
      padding-bottom: 4px;
    }}

    .card-content {{
      flex: 1;
      font-size: 11.5px;
      line-height: 1.48;
      color: #273849;
    }}

    /* Abstract Text */
    .abstract-text {{
      text-align: justify;
      color: #334155;
      font-size: 11.3px;
      line-height: 1.52;
    }}

    /* Bullet Lists */
    .bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 5.5px;
    }}

    .bullet-list li {{
      position: relative;
      padding-left: 14px;
      font-size: 11.2px;
      line-height: 1.42;
      color: #2c3e50;
    }}

    .bullet-list li::before {{
      content: '▪';
      position: absolute;
      left: 0;
      top: -1px;
      color: #1976d2;
      font-size: 14px;
    }}

    .bullet-list strong {{
      color: #0f2744;
      font-weight: 700;
    }}

    /* Objectives List with numbered badges */
    .objectives-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .objectives-list li {{
      display: flex;
      align-items: flex-start;
      gap: 7px;
      font-size: 11.1px;
      line-height: 1.39;
      color: #2c3e50;
    }}

    .obj-num {{
      background: #e3f2fd;
      color: #1565c0;
      font-weight: 800;
      font-size: 10px;
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid #bbdefb;
      margin-top: 1px;
      flex-shrink: 0;
    }}

    /* Methodology Diagram */
    .methodology-diagram {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      height: 100%;
    }}

    .flow-row {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .flow-step {{
      flex: 1;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 5px 6px;
      text-align: center;
    }}

    .flow-step-header {{
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      margin-bottom: 2px;
      color: #0f2744;
    }}

    .flow-step-desc {{
      font-size: 9.8px;
      color: #475569;
      line-height: 1.25;
    }}

    .flow-arrow {{
      font-size: 12px;
      font-weight: 900;
      color: #1976d2;
    }}

    .channel-box {{
      background: #f0f7ff;
      border: 1px solid #b8daff;
      border-radius: 5px;
      padding: 4px 7px;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 10.3px;
    }}
    .channel-title {{
      font-weight: 700;
      color: #0d47a1;
    }}
    .channel-model {{
      font-family: 'JetBrains Mono', monospace;
      background: #0d47a1;
      color: #fff;
      padding: 1px 6px;
      border-radius: 3px;
      font-size: 9.2px;
      font-weight: 700;
    }}

    .fusion-box {{
      background: linear-gradient(135deg, #e8f4fd, #e0f2fe);
      border: 1.5px dashed #0288d1;
      border-radius: 6px;
      padding: 5px 8px;
      text-align: center;
      font-size: 10.3px;
      font-weight: 600;
      color: #01579b;
    }}

    /* Table styling for Results */
    .results-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 10.4px;
      margin-bottom: 6px;
    }}

    .results-table th {{
      background: #0f2d4f;
      color: white;
      padding: 4px 6px;
      text-align: center;
      font-weight: 700;
      font-size: 9.8px;
      letter-spacing: 0.3px;
    }}
    .results-table th:first-child {{
      text-align: left;
    }}

    .results-table td {{
      padding: 3.5px 6px;
      border-bottom: 1px solid #e2e8f0;
      text-align: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
    }}
    .results-table td:first-child {{
      text-align: left;
      font-family: 'Inter', sans-serif;
      font-weight: 700;
      color: #0f2d4f;
    }}

    .results-table tr.highlight {{
      background: #e8f4fd;
    }}
    .results-table tr.highlight td {{
      color: #0d47a1;
      font-weight: 800;
    }}

    .metric-pills {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      margin-top: 5px;
    }}

    .pill {{
      background: #f1f8fe;
      border: 1px solid #bce0fd;
      border-radius: 5px;
      padding: 4px 7px;
      font-size: 9.8px;
      line-height: 1.32;
    }}
    .pill strong {{
      color: #0d47a1;
      font-weight: 800;
    }}

    /* Conclusion points */
    .conclusion-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 7px;
    }}
    .conclusion-list li {{
      position: relative;
      padding-left: 15px;
      font-size: 11.2px;
      line-height: 1.44;
      color: #273849;
    }}
    .conclusion-list li::before {{
      content: '✓';
      position: absolute;
      left: 0;
      top: -1px;
      color: #2e7d32;
      font-weight: 900;
      font-size: 13px;
    }}
    .conclusion-list strong {{
      color: #092240;
    }}

    /* Bottom Row (Applications & Final Outcome) */
    .bottom-row {{
      display: grid;
      grid-template-columns: 1fr 1.25fr;
      gap: 10px;
      min-height: 42px;
    }}

    .bottom-card {{
      background: var(--card-bg);
      border-radius: var(--border-radius);
      border: 1px solid var(--card-border);
      box-shadow: var(--box-shadow);
      padding: 8px 16px;
      display: flex;
      align-items: center;
      font-size: 11.6px;
      gap: 8px;
    }}

    .bottom-tag {{
      font-family: 'Outfit', sans-serif;
      font-size: 12px;
      font-weight: 900;
      color: var(--primary-navy);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }}

    .bottom-text {{
      color: #334155;
      font-weight: 500;
      line-height: 1.35;
    }}

    .bottom-text strong {{
      color: #0f2744;
      font-weight: 700;
    }}

    /* PRINT & PDF EXPORT STYLES */
    @media print {{
      body {{
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
      }}

      .top-toolbar {{
        display: none !important;
      }}

      .poster-viewport {{
        width: 100vw !important;
        height: 100vh !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        page-break-after: avoid;
        page-break-inside: avoid;
      }}

      @page {{
        size: A3 landscape;
        margin: 0mm;
      }}
    }}
  </style>
</head>
<body>

  <!-- Interactive Toolbar for Presentation & Printing -->
  <div class="top-toolbar">
    <div class="toolbar-title">
      <span>🎓 Global Academy of Technology</span>
      <span style="color: #64748b;">|</span>
      <span>Final Year Project Presentation Poster</span>
    </div>
    <div class="toolbar-actions">
      <button class="btn btn-secondary" onclick="toggleFullscreen()">
        🖥️ Fullscreen Mode
      </button>
      <button class="btn btn-green" onclick="window.print()">
        🖨️ Print / Save as PDF
      </button>
      <a href="http://localhost:5173" target="_blank" class="btn">
        🚀 Open Live App
      </a>
    </div>
  </div>

  <!-- The 16:9 Presentation Poster Canvas -->
  <div class="poster-viewport" id="posterCanvas">

    <!-- College Header -->
    <header class="poster-header">
      <div class="logo-box">
        <img src="data:image/png;base64,{logo_b64}" alt="Global Academy of Technology Logo" />
      </div>
      <div class="header-text-container">
        <h1 class="college-name">GLOBAL ACADEMY OF TECHNOLOGY</h1>
        <h2 class="dept-name">Department of Artificial Intelligence and Machine Learning</h2>
      </div>
    </header>

    <!-- Poster Content Canvas -->
    <main class="poster-body">

      <!-- Project Title Banner -->
      <section class="title-card">
        <div class="title-left">
          <span class="title-label">PROJECT TITLE:</span>
          <span class="title-text">Adaptive Multi-Modal Phishing Detection Using Deep Learning and Behavioural Anomaly Analysis</span>
        </div>
        <div class="title-sdg">
          <span>🌐</span>
          <span>SDGs: 9 (Industry, Innovation & Infrastructure) • 16 (Peace & Strong Institutions)</span>
        </div>
      </section>

      <!-- Team & Guide Banner -->
      <section class="team-card">
        <div class="team-members">
          <span class="tag">TEAM:</span>
          <span>Manishankar Dinesh Bhat • Sharanabasava • Pranav S</span>
        </div>
        <div class="team-guide">
          <span class="guide-tag">GUIDE:</span>
          <span>Ramya C, Assistant Professor, Dept. of AIML</span>
        </div>
      </section>

      <!-- 6-Card Main Section -->
      <div class="grid-container">

        <!-- CARD 1: ABSTRACT -->
        <article class="card">
          <h3 class="card-title">ABSTRACT</h3>
          <div class="card-content">
            <p class="abstract-text">
              Phishing is one of the most critical cybersecurity threats today, severely exacerbated by AI-crafted and zero-day campaigns that evade static rule-based filters. Traditional detection approaches rely on a single data source—such as URL attributes or email body text—leaving significant blind spots. To resolve this limitation, we present an <strong>Adaptive Multi-Modal Phishing Detection Framework</strong> combining deep learning and real-time user behavioural analytics. Our architecture integrates a fine-tuned <strong>BERT transformer</strong> for contextual email text classification, a deep <strong>Character-level CNN</strong> with 14 structural features for malicious URL detection, and an <strong>Isolation Forest</strong> algorithm for identifying abnormal browsing dynamics. Individual predictions are fused through an intelligent multi-tier risk engine, eliminating single-point vulnerabilities and delivering robust, zero-day threat protection with 99.3% accuracy.
            </p>
          </div>
        </article>

        <!-- CARD 2: PROBLEM STATEMENT -->
        <article class="card">
          <h3 class="card-title">PROBLEM STATEMENT</h3>
          <div class="card-content">
            <ul class="bullet-list">
              <li>
                <strong>Rise of AI-Generated Phishing:</strong> Attackers routinely exploit Large Language Models to craft grammatically flawless, contextually authentic zero-day lures without static signatures.
              </li>
              <li>
                <strong>Single-Source Blind Spots:</strong> Existing solutions analyze URLs or text in isolation; benign-looking emails containing stealthy links or clean URLs on compromised hosts slip through.
              </li>
              <li>
                <strong>Neglect of User Behavioural Cues:</strong> Traditional systems completely ignore post-click interactions (excessive redirects, abnormal mouse velocity, multiple failed login attempts).
              </li>
              <li>
                <strong>Fragility of Static Blacklists:</strong> Rule-based and whitelist techniques require continuous manual updating, degrade rapidly against new domains, and trigger frequent false positives.
              </li>
            </ul>
          </div>
        </article>

        <!-- CARD 3: OBJECTIVES -->
        <article class="card">
          <h3 class="card-title">OBJECTIVES</h3>
          <div class="card-content">
            <ul class="objectives-list">
              <li>
                <span class="obj-num">01</span>
                <div><strong>Email Semantic Detection:</strong> Train and fine-tune transformer-based <strong>BERT</strong> to capture contextual semantics and coercive social-engineering language.</div>
              </li>
              <li>
                <span class="obj-num">02</span>
                <div><strong>Character-Level URL Analysis:</strong> Develop a deep <strong>Character-Level CNN</strong> with 14 lexical & structural attributes to catch obfuscated zero-day URLs.</div>
              </li>
              <li>
                <span class="obj-num">03</span>
                <div><strong>Behavioural Anomaly Scoring:</strong> Implement an <strong>Isolation Forest</strong> engine to flag post-click anomalies across 8 user interaction features in real time.</div>
              </li>
              <li>
                <span class="obj-num">04</span>
                <div><strong>Adaptive Multi-Modal Fusion:</strong> Synthesize multi-source signals via an intelligent weighting scheme to produce a calibrated, explainable risk score.</div>
              </li>
            </ul>
          </div>
        </article>

        <!-- CARD 4: METHODOLOGY / WORKFLOW -->
        <article class="card">
          <h3 class="card-title">METHODOLOGY / WORKFLOW</h3>
          <div class="card-content methodology-diagram">
            <!-- Channels -->
            <div class="channel-box">
              <span class="channel-title">📧 Email Ingestion & Preprocessing</span>
              <span class="channel-model">BERT (Transformer)</span>
            </div>
            <div class="channel-box">
              <span class="channel-title">🔗 URL Lexical & Structural Parsing</span>
              <span class="channel-model">Char-CNN (14 Feats)</span>
            </div>
            <div class="channel-box">
              <span class="channel-title">🖱️ Telemetry & Interaction Monitoring</span>
              <span class="channel-model">Isolation Forest</span>
            </div>

            <!-- Workflow Pipeline Blocks -->
            <div class="flow-row" style="margin-top: 3px;">
              <div class="flow-step">
                <div class="flow-step-header">1. Preprocess</div>
                <div class="flow-step-desc">WordPiece Tokenizer & Min-Max Normalization</div>
              </div>
              <div class="flow-arrow">➔</div>
              <div class="flow-step">
                <div class="flow-step-header">2. Deep Inference</div>
                <div class="flow-step-desc">Self-Attention & 1D Convolutions</div>
              </div>
              <div class="flow-arrow">➔</div>
              <div class="flow-step">
                <div class="flow-step-header">3. Fusion & Risk</div>
                <div class="flow-step-desc">Non-Linear Dominant Weighting</div>
              </div>
            </div>

            <!-- Fusion Indicator -->
            <div class="fusion-box" style="margin-top: 5px;">
              <strong>Multi-Tier Output:</strong> Low Risk (&lt;0.35) • Suspicious (0.35–0.65) • Phishing (≥0.65)
            </div>
          </div>
        </article>

        <!-- CARD 5: EXPERIMENTAL RESULTS -->
        <article class="card">
          <h3 class="card-title">EXPERIMENTAL RESULTS</h3>
          <div class="card-content">
            <!-- Performance Table from Published Paper Table II -->
            <table class="results-table">
              <thead>
                <tr>
                  <th>Model & Modality</th>
                  <th>Accuracy</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1-Score</th>
                  <th>ROC-AUC</th>
                </tr>
              </thead>
              <tbody>
                <tr class="highlight">
                  <td>BERT (Email Text)</td>
                  <td>99.33%</td>
                  <td>99.60%</td>
                  <td>99.07%</td>
                  <td>99.34%</td>
                  <td>99.34%</td>
                </tr>
                <tr class="highlight">
                  <td>CNN (URL Analysis)</td>
                  <td>96.70%</td>
                  <td>96.27%</td>
                  <td>97.22%</td>
                  <td>96.74%</td>
                  <td>99.51%</td>
                </tr>
                <tr>
                  <td>BiLSTM (Email Text)</td>
                  <td>98.93%</td>
                  <td>99.33%</td>
                  <td>98.54%</td>
                  <td>98.94%</td>
                  <td>97.15%</td>
                </tr>
                <tr>
                  <td>LSTM (Email Text)</td>
                  <td>93.05%</td>
                  <td>90.89%</td>
                  <td>95.84%</td>
                  <td>93.30%</td>
                  <td>98.30%</td>
                </tr>
              </tbody>
            </table>

            <!-- Performance Badges -->
            <div class="metric-pills">
              <div class="pill">
                <strong>BERT Dominance:</strong> Highest MCC (98.67%) with exceptional false-positive suppression on business notifications.
              </div>
              <div class="pill">
                <strong>CNN URL Efficacy:</strong> 99.51% ROC-AUC on detecting obfuscated, deep-nested subdomains and brand lures.
              </div>
            </div>
          </div>
        </article>

        <!-- CARD 6: CONCLUSION -->
        <article class="card">
          <h3 class="card-title">CONCLUSION</h3>
          <div class="card-content">
            <ul class="conclusion-list">
              <li>
                <strong>Eliminates Single-Vector Blind Spots:</strong> Concurrently evaluating linguistic content, URL patterns, and user telemetry reliably defeats sophisticated multi-stage attacks.
              </li>
              <li>
                <strong>Proven State-of-the-Art Accuracy:</strong> BERT achieved 99.33% accuracy on emails while CNN reached 99.51% ROC-AUC on URLs, confirming deep architectures outperform classical ML.
              </li>
              <li>
                <strong>Behavioural Safety Net:</strong> Isolation Forest adds an invaluable post-click layer, flagging rapid redirects and abnormal interactions even when content appears benign.
              </li>
            </ul>
          </div>
        </article>

      </div>

      <!-- Bottom Banners -->
      <footer class="bottom-row">
        <div class="bottom-card">
          <span class="bottom-tag">APPLICATIONS:</span>
          <span class="bottom-text">
            Enterprise Email Gateways • Endpoint Web Browser Extensions • Banking & Fintech Real-Time Anti-Fraud Defense Systems
          </span>
        </div>
        <div class="bottom-card">
          <span class="bottom-tag">OUTCOME:</span>
          <span class="bottom-text">
            A unified multi-modal cybersecurity framework fusing BERT, Character CNN, and Isolation Forest to deliver high-confidence, real-time zero-day phishing protection with <strong>99.3% accuracy</strong>.
          </span>
        </div>
      </footer>

    </main>

  </div>

  <script>
    function toggleFullscreen() {{
      const elem = document.getElementById('posterCanvas');
      if (!document.fullscreenElement) {{
        if (elem.requestFullscreen) {{
          elem.requestFullscreen();
        }} else if (elem.webkitRequestFullscreen) {{
          elem.webkitRequestFullscreen();
        }}
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen();
        }}
      }}
    }}
  </script>
</body>
</html>
'''

os.makedirs(r'c:\Docs\Phishing_Detection\poster', exist_ok=True)
with open(r'c:\Docs\Phishing_Detection\poster\index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Successfully created poster/index.html!')
