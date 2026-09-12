from typing import Dict, Optional


# ============================================================
# THRESHOLDS (CALIBRATED FOR REDUCED FP AND FN)
# ============================================================

RISK_THRESHOLDS = {
    "low": 0.35,
    "medium": 0.65,
    "high": 0.80,
    "critical": 0.85,
}

# A warning / stepped-up caution threshold starts here.
WARNING_THRESHOLD = 0.55

# A confirmed phishing classification threshold.
PHISHING_THRESHOLD = 0.65

# Individual model score considered a strong phishing signal.
STRONG_SIGNAL_THRESHOLD = 0.65


# ============================================================
# VALIDATE SCORE
# ============================================================

def validate_score(
    score: float,
    name: str
) -> float:

    try:
        score = float(score)

    except (TypeError, ValueError):
        raise ValueError(
            f"{name} must be numeric."
        )

    if not 0.0 <= score <= 1.0:
        raise ValueError(
            f"{name} must be between 0 and 1."
        )

    return score


# ============================================================
# RISK LEVEL
# ============================================================

def determine_risk_level(
    fused_score: float
) -> str:

    if fused_score < RISK_THRESHOLDS["low"]:
        return "low"

    if fused_score < RISK_THRESHOLDS["medium"]:
        return "medium"

    if fused_score < RISK_THRESHOLDS["high"]:
        return "high"

    return "critical"


# ============================================================
# SEVERITY
# ============================================================

def calculate_severity(
    fused_score: float
) -> str:

    if fused_score < 0.20:
        return "very_low"

    if fused_score < 0.40:
        return "low"

    if fused_score < 0.60:
        return "moderate"

    if fused_score < 0.80:
        return "high"

    if fused_score < 0.90:
        return "very_high"

    return "extreme"


# ============================================================
# MODEL AGREEMENT
# ============================================================

def normalize_agreement(
    model_agreement
) -> str:

    if isinstance(model_agreement, dict):
        return str(
            model_agreement.get(
                "agreement",
                "unknown"
            )
        ).lower()

    if isinstance(model_agreement, str):
        return model_agreement.lower()

    return "unknown"


# ============================================================
# ACTIVE MODELS
# ============================================================

def get_active_models(
    email_score: float,
    url_score: float,
    behavior_score: float,
    mode: str,
    weights: Optional[Dict] = None
) -> Dict:

    scores = {
        "email": email_score,
        "url": url_score,
        "behavior": behavior_score,
    }

    # If fusion weights are supplied, only models with
    # positive weights are considered active.
    if weights:
        active = [
            name
            for name, weight in weights.items()
            if name in scores and float(weight) > 0
        ]

    else:

        mode = str(mode).lower()

        if mode == "website":
            active = [
                "url",
                "behavior",
            ]

        else:
            active = [
                "email",
                "url",
                "behavior",
            ]

    return {
        name: scores[name]
        for name in active
        if name in scores
    }


# ============================================================
# STRONG SIGNAL COUNT
# ============================================================

def count_strong_signals(
    active_models: Dict
) -> int:

    return sum(
        1
        for score in active_models.values()
        if score >= STRONG_SIGNAL_THRESHOLD
    )


# ============================================================
# MODEL CONFIDENCE
# ============================================================

def calculate_model_confidence(
    active_models: Dict
) -> float:

    if not active_models:
        return 0.0

    scores = np.array(
        list(active_models.values()),
        dtype=np.float32
    )

    # One model alone can still be highly confident,
    # but we do not pretend that cross-model agreement exists.
    if len(scores) == 1:

        score = float(scores[0])

        confidence = (
            0.50 +
            abs(score - 0.50)
        )

        return float(
            np.clip(
                confidence,
                0.0,
                1.0
            )
        )

    standard_deviation = float(
        np.std(scores)
    )

    disagreement = min(
        standard_deviation / 0.50,
        1.0
    )

    confidence = (
        1.0 -
        disagreement
    )

    return float(
        np.clip(
            confidence,
            0.0,
            1.0
        )
    )


# ============================================================
# FINAL CLASSIFICATION
# ============================================================

def determine_classification(
    fused_score: float,
    active_models: Dict,
    model_agreement: str
) -> str:

    # Clean score under baseline is confirmed legitimate.
    if fused_score < RISK_THRESHOLDS["low"]:
        return "legitimate"

    strong_signals = count_strong_signals(
        active_models
    )

    # High fused score with at least one strong model signal is phishing
    if (
        fused_score >= PHISHING_THRESHOLD
        and
        strong_signals >= 1
    ):
        return "phishing"

    # Definitively high fused score
    if fused_score >= 0.75:
        return "phishing"

    # Moderate/ambiguous score represents suspicious activity requiring caution
    return "suspicious"


# ============================================================
# WARNING DECISION
# ============================================================

def determine_warning_required(
    fused_score: float
) -> bool:

    return fused_score >= WARNING_THRESHOLD


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def determine_action(
    risk_level: str,
    warning_required: bool,
    classification: str
) -> str:

    if not warning_required:

        if classification == "suspicious":
            return "Proceed with caution"

        return "Allow access"

    if classification == "phishing":
        return "Block or strongly warn user"

    return "Warn user before continuing"


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(
    fused_score: float,
    email_score: float,
    url_score: float,
    behavior_score: float,
    model_agreement: Optional[Dict] = None,
    mode: str = "email",
    weights: Optional[Dict] = None
) -> Dict:

    fused_score = validate_score(
        fused_score,
        "Fused score"
    )

    email_score = validate_score(
        email_score,
        "Email score"
    )

    url_score = validate_score(
        url_score,
        "URL score"
    )

    behavior_score = validate_score(
        behavior_score,
        "Behavior score"
    )

    agreement_level = normalize_agreement(
        model_agreement
    )

    active_models = get_active_models(
        email_score=email_score,
        url_score=url_score,
        behavior_score=behavior_score,
        mode=mode,
        weights=weights
    )

    confidence = calculate_model_confidence(
        active_models
    )

    classification = determine_classification(
        fused_score=fused_score,
        active_models=active_models,
        model_agreement=agreement_level
    )

    risk_level = determine_risk_level(
        fused_score
    )

    severity = calculate_severity(
        fused_score
    )

    warning_required = determine_warning_required(
        fused_score
    )

    action = determine_action(
        risk_level=risk_level,
        warning_required=warning_required,
        classification=classification
    )

    model_scores = {
        "email": email_score,
        "url": url_score,
        "behavior": behavior_score,
    }

    strong_signals = count_strong_signals(
        active_models
    )

    return {

        # ----------------------------------------------------
        # PRIMARY RISK
        # ----------------------------------------------------

        "risk_score": round(
            fused_score,
            6
        ),

        "risk_percentage": round(
            fused_score * 100,
            2
        ),

        "risk_level": risk_level,

        "severity": severity,

        # ----------------------------------------------------
        # FINAL CLASSIFICATION
        # ----------------------------------------------------

        "classification": classification,

        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

        "confidence": round(
            confidence,
            4
        ),

        "confidence_percentage": round(
            confidence * 100,
            2
        ),

        # ----------------------------------------------------
        # MODEL INFORMATION
        # ----------------------------------------------------

        "model_agreement": agreement_level,

        "model_scores": model_scores,

        "active_models": list(
            active_models.keys()
        ),

        "strong_signal_count": strong_signals,

        # ----------------------------------------------------
        # EXTENSION DECISION
        # ----------------------------------------------------

        "warning_required": warning_required,

        "recommended_action": action,

        # ----------------------------------------------------
        # EXPLICIT USER ACTION
        # ----------------------------------------------------

        "allow_access": not warning_required,

        "requires_confirmation": warning_required,

        # ----------------------------------------------------
        # THRESHOLDS USED
        # ----------------------------------------------------

        "thresholds": {
            "warning": WARNING_THRESHOLD,
            "phishing": PHISHING_THRESHOLD,
            "strong_signal": STRONG_SIGNAL_THRESHOLD,
        },
    }


# ============================================================
# COMPLETE RISK ANALYSIS
# ============================================================

def analyze_risk(
    fusion_result: Dict
) -> Dict:

    if not isinstance(
        fusion_result,
        dict
    ):
        raise ValueError(
            "fusion_result must be a dictionary."
        )

    if "fused_score" not in fusion_result:
        raise ValueError(
            "Fusion result does not contain fused_score."
        )

    models = fusion_result.get(
        "models",
        {}
    )

    model_scores = fusion_result.get(
        "model_scores",
        {}
    )

    email_data = models.get(
        "email",
        {}
    )

    url_data = models.get(
        "url",
        {}
    )

    behavior_data = models.get(
        "behavior",
        {}
    )

    email_score = model_scores.get(
        "email",
        email_data.get(
            "score",
            0.0
        )
    )

    url_score = model_scores.get(
        "url",
        url_data.get(
            "score",
            0.0
        )
    )

    behavior_score = model_scores.get(
        "behavior",
        behavior_data.get(
            "score",
            0.0
        )
    )

    email_score = validate_score(
        email_score,
        "Email score"
    )

    url_score = validate_score(
        url_score,
        "URL score"
    )

    behavior_score = validate_score(
        behavior_score,
        "Behavior score"
    )

    mode = str(
        fusion_result.get(
            "mode",
            "email"
        )
    ).lower()

    weights = fusion_result.get(
        "weights",
        {}
    )

    if not isinstance(weights, dict):
        weights = {}

    result = calculate_risk(
        fused_score=fusion_result["fused_score"],
        email_score=email_score,
        url_score=url_score,
        behavior_score=behavior_score,
        model_agreement=fusion_result.get(
            "model_agreement"
        ),
        mode=mode,
        weights=weights
    )

    # ========================================================
    # MODEL CONTRIBUTIONS
    # ========================================================

    contributions = fusion_result.get(
        "model_contributions",
        {}
    )

    if not isinstance(contributions, dict):
        contributions = {}

    if not contributions:

        contributions = {
            "email": (
                email_score *
                float(
                    weights.get(
                        "email",
                        0.0
                    )
                )
            ),

            "url": (
                url_score *
                float(
                    weights.get(
                        "url",
                        0.0
                    )
                )
            ),

            "behavior": (
                behavior_score *
                float(
                    weights.get(
                        "behavior",
                        0.0
                    )
                )
            ),
        }

    # Keep contribution values inside [0, 1].
    contributions = {
        name: float(
            np.clip(
                value,
                0.0,
                1.0
            )
        )
        for name, value in contributions.items()
    }

    # ========================================================
    # ACTIVE CONTRIBUTIONS
    # ========================================================

    active_contributions = {
        name: value
        for name, value in contributions.items()
        if float(
            weights.get(
                name,
                0.0
            )
        ) > 0.0
    }

    # If no weights were supplied, use active models instead.
    if not active_contributions:

        active_contributions = {
            name: value
            for name, value in contributions.items()
            if name in result["active_models"]
        }

    # ========================================================
    # DOMINANT MODEL
    # ========================================================

    if active_contributions:

        dominant_model = max(
            active_contributions,
            key=active_contributions.get
        )

    else:
        dominant_model = "unknown"

    result["model_contributions"] = contributions

    result["dominant_model"] = dominant_model

    result["dominant_model_score"] = float(
        result["model_scores"].get(
            dominant_model,
            0.0
        )
    )

    # ========================================================
    # DIAGNOSTICS
    # ========================================================

    raw_scores = result["model_scores"]

    if raw_scores:

        highest_raw_signal = max(
            raw_scores,
            key=raw_scores.get
        )

    else:
        highest_raw_signal = "unknown"

    sorted_contributions = sorted(
        active_contributions.values(),
        reverse=True
    )

    score_gap = 0.0

    if len(sorted_contributions) >= 2:

        score_gap = round(
            sorted_contributions[0]
            -
            sorted_contributions[1],
            4
        )

    result["diagnostic"] = {

        "highest_raw_signal":
            highest_raw_signal,

        "highest_weighted_signal":
            dominant_model,

        "score_gap_from_next":
            score_gap,

        "active_model_count":
            len(result["active_models"]),

        "strong_signal_count":
            result["strong_signal_count"],
    }

    return result


# ============================================================
# DISPLAY
# ============================================================

def display_risk(
    result: Dict
):

    print(
        "\n" +
        "=" * 70
    )

    print(
        "RISK SCORING RESULT"
    )

    print(
        "=" * 70
    )

    print(
        f"\nRisk Score       : "
        f"{result['risk_percentage']:.2f}%"
    )

    print(
        f"Risk Level       : "
        f"{result['risk_level'].upper()}"
    )

    print(
        f"Severity         : "
        f"{result['severity'].upper()}"
    )

    print(
        f"Classification   : "
        f"{result['classification'].upper()}"
    )

    print(
        f"Confidence       : "
        f"{result['confidence_percentage']:.2f}%"
    )

    print(
        f"Model Agreement  : "
        f"{str(result['model_agreement']).upper()}"
    )

    print(
        f"Warning Required : "
        f"{result['warning_required']}"
    )

    print(
        f"Recommended      : "
        f"{result['recommended_action']}"
    )

    print(
        "\nModel Scores:"
    )

    for name, score in result[
        "model_scores"
    ].items():

        print(
            f"  {name.capitalize():12}: "
            f"{score * 100:.2f}%"
        )

    print(
        "\nActive Models:"
    )

    for model in result[
        "active_models"
    ]:

        print(
            f"  - {model}"
        )

    print(
        "\nDominant Model   : "
        f"{result.get('dominant_model', 'unknown')}"
    )

    print(
        "=" * 70
    )


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 70
    )

    print(
        "RISK SCORING ENGINE TEST"
    )

    print(
        "=" * 70
    )

    try:

        fused_score = (
            float(
                input(
                    "\nFused score (0-100%): "
                )
            ) / 100
        )

        email_score = (
            float(
                input(
                    "BERT / Email score (0-100%): "
                )
            ) / 100
        )

        url_score = (
            float(
                input(
                    "CNN / URL score (0-100%): "
                )
            ) / 100
        )

        behavior_score = (
            float(
                input(
                    "Isolation Forest / Behavior score (0-100%): "
                )
            ) / 100
        )

        result = calculate_risk(
            fused_score=fused_score,
            email_score=email_score,
            url_score=url_score,
            behavior_score=behavior_score
        )

        display_risk(
            result
        )

    except ValueError as exc:

        print(
            f"\nInput error: {exc}"
        )