from typing import Dict, List, Any


# ============================================================
# CONFIGURATION
# ============================================================

HIGH_THRESHOLD = 0.70
MEDIUM_THRESHOLD = 0.40


# ============================================================
# SCORE LABEL
# ============================================================

def score_label(score: float) -> str:

    if score >= HIGH_THRESHOLD:
        return "high"

    if score >= MEDIUM_THRESHOLD:
        return "medium"

    return "low"


# ============================================================
# EMAIL EXPLANATION
# ============================================================

def explain_email(
    email_score: float,
    email_text: str = ""
) -> List[Dict[str, Any]]:

    reasons = []

    if email_score >= 0.90:

        reasons.append({
            "source": "email",
            "severity": "critical",
            "reason": (
                "BERT detected a very high probability "
                "of phishing in the email content."
            ),
            "score": email_score,
        })

    elif email_score >= 0.70:

        reasons.append({
            "source": "email",
            "severity": "high",
            "reason": (
                "BERT detected strong phishing indicators "
                "in the email content."
            ),
            "score": email_score,
        })

    elif email_score >= 0.40:

        reasons.append({
            "source": "email",
            "severity": "medium",
            "reason": (
                "The email contains content patterns "
                "that require caution."
            ),
            "score": email_score,
        })

    else:

        reasons.append({
            "source": "email",
            "severity": "low",
            "reason": (
                "BERT found relatively low phishing "
                "probability in the email content."
            ),
            "score": email_score,
        })

    return reasons


# ============================================================
# URL EXPLANATION
# ============================================================

def explain_url(
    url_score: float,
    url_features: Dict[str, Any]
) -> List[Dict[str, Any]]:

    reasons = []

    if url_score >= 0.70:

        reasons.append({
            "source": "url",
            "severity": "high",
            "reason": (
                "The URL model detected strong phishing "
                "characteristics."
            ),
            "score": url_score,
        })

    elif url_score >= 0.40:

        reasons.append({
            "source": "url",
            "severity": "medium",
            "reason": (
                "The URL contains characteristics that "
                "require caution."
            ),
            "score": url_score,
        })

    else:

        reasons.append({
            "source": "url",
            "severity": "low",
            "reason": (
                "The URL model found relatively low "
                "phishing probability."
            ),
            "score": url_score,
        })

    # --------------------------------------------------------
    # URL LENGTH
    # --------------------------------------------------------

    url_length = url_features.get(
        "url_length"
    )

    if url_length is not None:

        if url_length > 100:

            reasons.append({
                "source": "url",
                "severity": "medium",
                "reason": (
                    f"The URL is unusually long "
                    f"({url_length} characters)."
                ),
                "feature": "url_length",
                "value": url_length,
            })

    # --------------------------------------------------------
    # SUSPICIOUS KEYWORDS
    # --------------------------------------------------------

    suspicious_keywords = url_features.get(
        "suspicious_keyword_count"
    )

    if suspicious_keywords is not None:

        if suspicious_keywords > 0:

            reasons.append({
                "source": "url",
                "severity": "high",
                "reason": (
                    f"The URL contains "
                    f"{suspicious_keywords} suspicious "
                    f"keyword(s)."
                ),
                "feature": (
                    "suspicious_keyword_count"
                ),
                "value": suspicious_keywords,
            })

    # --------------------------------------------------------
    # SUBDOMAINS
    # --------------------------------------------------------

    subdomain_count = url_features.get(
        "subdomain_count"
    )

    if subdomain_count is not None:

        if subdomain_count >= 4:

            reasons.append({
                "source": "url",
                "severity": "medium",
                "reason": (
                    f"The URL contains an unusually high "
                    f"number of subdomains ({subdomain_count})."
                ),
                "feature": "subdomain_count",
                "value": subdomain_count,
            })

    # --------------------------------------------------------
    # TLD RISK
    # --------------------------------------------------------

    tld_risk = url_features.get(
        "tld_risk_score"
    )

    if tld_risk is not None:

        if tld_risk > 0:

            reasons.append({
                "source": "url",
                "severity": "high",
                "reason": (
                    "The URL uses a TLD associated with "
                    "higher phishing risk in the training "
                    "features."
                ),
                "feature": "tld_risk_score",
                "value": tld_risk,
            })

    # --------------------------------------------------------
    # HTTPS
    # --------------------------------------------------------

    https_flag = url_features.get(
        "https_flag"
    )

    if https_flag == 0:

        reasons.append({
            "source": "url",
            "severity": "medium",
            "reason": (
                "The URL does not use HTTPS."
            ),
            "feature": "https_flag",
            "value": https_flag,
        })

    # --------------------------------------------------------
    # DIGIT RATIO
    # --------------------------------------------------------

    digit_ratio = url_features.get(
        "digit_ratio"
    )

    if digit_ratio is not None:

        if digit_ratio > 0.30:

            reasons.append({
                "source": "url",
                "severity": "medium",
                "reason": (
                    "The URL contains an unusually "
                    "high proportion of digits."
                ),
                "feature": "digit_ratio",
                "value": digit_ratio,
            })

    # --------------------------------------------------------
    # HYPHENS
    # --------------------------------------------------------

    hyphens = url_features.get(
        "number_of_hyphens"
    )

    if hyphens is not None:

        if hyphens >= 3:

            reasons.append({
                "source": "url",
                "severity": "medium",
                "reason": (
                    f"The URL contains many hyphens "
                    f"({hyphens})."
                ),
                "feature": "number_of_hyphens",
                "value": hyphens,
            })

    return reasons


# ============================================================
# BEHAVIOR EXPLANATION
# ============================================================

def explain_behavior(
    behavior_score: float,
    behavior_features: Dict[str, Any]
) -> List[Dict[str, Any]]:

    reasons = []

    # --------------------------------------------------------
    # OVERALL ANOMALY
    # --------------------------------------------------------

    if behavior_score >= 0.80:

        reasons.append({
            "source": "behavior",
            "severity": "critical",
            "reason": (
                "The observed browsing behavior is "
                "highly anomalous."
            ),
            "score": behavior_score,
        })

    elif behavior_score >= 0.60:

        reasons.append({
            "source": "behavior",
            "severity": "high",
            "reason": (
                "The observed browsing behavior shows "
                "significant anomalies."
            ),
            "score": behavior_score,
        })

    elif behavior_score >= 0.40:

        reasons.append({
            "source": "behavior",
            "severity": "medium",
            "reason": (
                "The observed browsing behavior contains "
                "some anomalous characteristics."
            ),
            "score": behavior_score,
        })

    else:

        reasons.append({
            "source": "behavior",
            "severity": "low",
            "reason": (
                "The observed behavior is relatively "
                "normal."
            ),
            "score": behavior_score,
        })

    # --------------------------------------------------------
    # CLICKS
    # --------------------------------------------------------

    clicks = behavior_features.get(
        "num_clicks"
    )

    if clicks is not None:

        if clicks > 50:

            reasons.append({
                "source": "behavior",
                "severity": "medium",
                "reason": (
                    f"An unusually high number of clicks "
                    f"was observed ({clicks:.2f})."
                ),
                "feature": "num_clicks",
                "value": clicks,
            })

    # --------------------------------------------------------
    # REDIRECTS
    # --------------------------------------------------------

    redirects = behavior_features.get(
        "num_redirects"
    )

    if redirects is not None:

        if redirects > 5:

            reasons.append({
                "source": "behavior",
                "severity": "high",
                "reason": (
                    f"Multiple redirects were observed "
                    f"({redirects:.2f})."
                ),
                "feature": "num_redirects",
                "value": redirects,
            })

    # --------------------------------------------------------
    # FAILED LOGINS
    # --------------------------------------------------------

    failed_logins = behavior_features.get(
        "failed_logins"
    )

    if failed_logins is not None:

        if failed_logins > 2:

            reasons.append({
                "source": "behavior",
                "severity": "high",
                "reason": (
                    f"Multiple failed login attempts "
                    f"were observed ({failed_logins:.2f})."
                ),
                "feature": "failed_logins",
                "value": failed_logins,
            })

    # --------------------------------------------------------
    # TAB SWITCHES
    # --------------------------------------------------------

    tab_switches = behavior_features.get(
        "tab_switches"
    )

    if tab_switches is not None:

        if tab_switches > 10:

            reasons.append({
                "source": "behavior",
                "severity": "medium",
                "reason": (
                    f"Frequent tab switching was observed "
                    f"({tab_switches:.2f})."
                ),
                "feature": "tab_switches",
                "value": tab_switches,
            })

    return reasons


# ============================================================
# MODEL AGREEMENT EXPLANATION
# ============================================================

def explain_model_agreement(
    model_agreement: Dict
) -> List[Dict[str, Any]]:

    reasons = []

    agreement = model_agreement.get(
        "agreement",
        "unknown"
    )

    if agreement == "high":

        reasons.append({
            "source": "fusion",
            "severity": "high",
            "reason": (
                "The email, URL, and behavioral models "
                "show strong agreement."
            ),
        })

    elif agreement == "moderate":

        reasons.append({
            "source": "fusion",
            "severity": "medium",
            "reason": (
                "The models show moderate agreement, "
                "with some differences in their scores."
            ),
        })

    elif agreement == "low":

        reasons.append({
            "source": "fusion",
            "severity": "medium",
            "reason": (
                "The models disagree significantly. "
                "The final result should therefore be "
                "interpreted with additional caution."
            ),
        })

    return reasons


# ============================================================
# SORT EXPLANATIONS
# ============================================================

def sort_reasons(
    reasons: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    severity_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    return sorted(
        reasons,
        key=lambda item: severity_order.get(
            item.get(
                "severity",
                "low"
            ),
            0
        ),
        reverse=True
    )


# ============================================================
# COMPLETE EXPLANATION
# ============================================================

def generate_explanation(
    email_score: float,
    url_score: float,
    behavior_score: float,
    url_features: Dict[str, Any],
    behavior_features: Dict[str, Any],
    model_agreement: Dict
) -> Dict[str, Any]:

    all_reasons = []

    email_reasons = explain_email(
        email_score
    )

    url_reasons = explain_url(
        url_score,
        url_features
    )

    behavior_reasons = explain_behavior(
        behavior_score,
        behavior_features
    )

    agreement_reasons = explain_model_agreement(
        model_agreement
    )

    all_reasons.extend(
        email_reasons
    )

    all_reasons.extend(
        url_reasons
    )

    all_reasons.extend(
        behavior_reasons
    )

    all_reasons.extend(
        agreement_reasons
    )

    all_reasons = sort_reasons(
        all_reasons
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    critical_count = sum(
        1
        for reason in all_reasons
        if reason.get("severity") == "critical"
    )

    high_count = sum(
        1
        for reason in all_reasons
        if reason.get("severity") == "high"
    )

    medium_count = sum(
        1
        for reason in all_reasons
        if reason.get("severity") == "medium"
    )

    if critical_count > 0:

        summary = (
            "Critical phishing indicators were detected."
        )

    elif high_count >= 2:

        summary = (
            "Multiple strong phishing indicators "
            "were detected."
        )

    elif high_count == 1:

        summary = (
            "A significant phishing indicator "
            "was detected."
        )

    elif medium_count > 0:

        summary = (
            "Some suspicious characteristics were "
            "detected and caution is recommended."
        )

    else:

        summary = (
            "No strong phishing indicators were detected."
        )

    return {
        "summary": summary,

        "total_reasons": len(
            all_reasons
        ),

        "critical_reasons": critical_count,

        "high_reasons": high_count,

        "medium_reasons": medium_count,

        "reasons": all_reasons,
    }


# ============================================================
# DISPLAY
# ============================================================

def display_explanation(
    result: Dict[str, Any]
):

    print("\n" + "=" * 60)
    print("EXPLAINABILITY RESULT")
    print("=" * 60)

    print(
        f"\nSummary:"
    )

    print(
        f"  {result['summary']}"
    )

    print(
        f"\nTotal reasons: "
        f"{result['total_reasons']}"
    )

    print("\nDetected Indicators:")

    for index, reason in enumerate(
        result["reasons"],
        start=1
    ):

        print(
            f"\n{index}. "
            f"[{reason.get('severity', 'low').upper()}] "
            f"{reason.get('source', 'unknown').upper()}"
        )

        print(
            f"   {reason['reason']}"
        )

        if "feature" in reason:

            print(
                f"   Feature: "
                f"{reason['feature']}"
            )

            print(
                f"   Value: "
                f"{reason['value']}"
            )

    print("=" * 60)


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("EXPLAINABILITY ENGINE TEST")
    print("=" * 60)

    email_score = float(
        input(
            "\nBERT / Email score (0-100%): "
        )
    ) / 100

    url_score = float(
        input(
            "CNN / URL score (0-100%): "
        )
    ) / 100

    behavior_score = float(
        input(
            "Isolation Forest / Behavior score (0-100%): "
        )
    ) / 100

    url_features = {
        "url_length": float(
            input(
                "\nURL length: "
            )
        ),

        "digit_ratio": float(
            input(
                "Digit ratio: "
            )
        ),

        "suspicious_keyword_count": int(
            input(
                "Suspicious keyword count: "
            )
        ),

        "subdomain_count": int(
            input(
                "Subdomain count: "
            )
        ),

        "tld_risk_score": int(
            input(
                "TLD risk score (0/1): "
            )
        ),

        "https_flag": int(
            input(
                "HTTPS flag (0/1): "
            )
        ),

        "number_of_hyphens": int(
            input(
                "Number of hyphens: "
            )
        ),
    }

    behavior_features = {
        "num_clicks": float(
            input(
                "\nNumber of clicks: "
            )
        ),

        "num_redirects": float(
            input(
                "Number of redirects: "
            )
        ),

        "failed_logins": float(
            input(
                "Failed logins: "
            )
        ),

        "tab_switches": float(
            input(
                "Tab switches: "
            )
        ),
    }

    model_agreement = {
        "agreement": "high"
    }

    result = generate_explanation(
        email_score=email_score,
        url_score=url_score,
        behavior_score=behavior_score,
        url_features=url_features,
        behavior_features=behavior_features,
        model_agreement=model_agreement,
    )

    display_explanation(
        result
    )