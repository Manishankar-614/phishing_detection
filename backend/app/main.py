from typing import Dict, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.email_predictor import predict_email
from app.url_predictor import predict_url
from app.behavior_predictor import predict_behavior

from app.feature_fusion import create_fusion_result
from app.risk.risk_scoring import analyze_risk


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Adaptive Multi-Modal Phishing Detection API",
    description="Backend API for the hybrid phishing detection system",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class BehaviorData(BaseModel):
    num_clicks: float = Field(default=0.0, ge=0)
    time_on_page: float = Field(default=0.0, ge=0)
    num_redirects: float = Field(default=0.0, ge=0)
    failed_logins: float = Field(default=0.0, ge=0)
    mouse_speed: float = Field(default=0.0, ge=0)
    typing_speed: float = Field(default=0.0, ge=0)
    tab_switches: float = Field(default=0.0, ge=0)


class AnalyzeRequest(BaseModel):
    url: Optional[str] = None
    email_text: Optional[str] = None
    behavior: Optional[BehaviorData] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def build_reasons(
    email_result: Optional[Dict[str, Any]],
    url_result: Optional[Dict[str, Any]],
    behavior_result: Optional[Dict[str, Any]],
    risk_result: Dict[str, Any]
):
    """
    Build human-readable reasons for the extension.
    """

    reasons = []

    risk_score = risk_result.get(
        "risk_score",
        0.0
    )

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if email_result is not None:

        email_score = float(
            email_result.get(
                "phishing_score",
                0.0
            )
        )

        if email_score >= 0.70:

            reasons.append({
                "severity": "high",
                "source": "email",
                "message":
                    "BERT detected a high probability of phishing "
                    "in the email content."
            })

        elif email_score >= 0.40:

            reasons.append({
                "severity": "medium",
                "source": "email",
                "message":
                    "BERT detected suspicious characteristics "
                    "in the email content."
            })

        else:

            reasons.append({
                "severity": "low",
                "source": "email",
                "message":
                    "BERT found relatively low phishing probability "
                    "in the email content."
            })

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    if url_result is not None:

        url_score = float(
            url_result.get(
                "url_score",
                0.0
            )
        )

        if url_score >= 0.70:

            reasons.append({
                "severity": "high",
                "source": "url",
                "message":
                    "The URL model detected strong phishing "
                    "characteristics."
            })

        elif url_score >= 0.40:

            reasons.append({
                "severity": "medium",
                "source": "url",
                "message":
                    "The URL contains suspicious characteristics."
            })

        else:

            reasons.append({
                "severity": "low",
                "source": "url",
                "message":
                    "The URL model found relatively low phishing risk."
            })

    # --------------------------------------------------------
    # BEHAVIOR
    # --------------------------------------------------------

    if behavior_result is not None:

        behavior_score = float(
            behavior_result.get(
                "behavior_score",
                0.0
            )
        )

        if behavior_score >= 0.70:

            reasons.append({
                "severity": "high",
                "source": "behavior",
                "message":
                    "The observed browsing behavior shows "
                    "significant anomalies."
            })

        elif behavior_score >= 0.40:

            reasons.append({
                "severity": "medium",
                "source": "behavior",
                "message":
                    "The observed browsing behavior contains "
                    "some suspicious patterns."
            })

        else:

            reasons.append({
                "severity": "low",
                "source": "behavior",
                "message":
                    "The observed browsing behavior appears "
                    "relatively normal."
            })

    # --------------------------------------------------------
    # MODEL AGREEMENT
    # --------------------------------------------------------

    agreement = str(
        risk_result.get(
            "model_agreement",
            "unknown"
        )
    ).lower()

    if agreement in (
        "high",
        "very_high"
    ) and risk_score >= 0.70:

        reasons.append({
            "severity": "high",
            "source": "fusion",
            "message":
                "The active detection models show strong agreement "
                "that the webpage may be unsafe."
        })

    elif agreement == "low" and risk_score >= 0.40:

        reasons.append({
            "severity": "medium",
            "source": "fusion",
            "message":
                "The detection models disagree significantly. "
                "The result should be interpreted with caution."
        })

    return reasons


def get_active_model_scores(
    risk_result: Dict[str, Any]
):

    scores = risk_result.get(
        "model_scores",
        {}
    )

    return {
        "email": round(
            float(scores.get("email", 0.0)) * 100,
            2
        ),
        "url": round(
            float(scores.get("url", 0.0)) * 100,
            2
        ),
        "behavior": round(
            float(scores.get("behavior", 0.0)) * 100,
            2
        )
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name":
            "Hybrid Phishing Detection API",

        "status":
            "running",

        "pipeline": [
            "BERT",
            "CNN",
            "Isolation Forest",
            "Feature Fusion",
            "Risk Scoring",
            "Explainability"
        ]
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
def analyze(request: AnalyzeRequest):

    try:

        # ====================================================
        # VALIDATION
        # ====================================================

        if not request.url and not request.email_text:

            raise HTTPException(
                status_code=400,
                detail="URL or email_text is required."
            )


        # ====================================================
        # INITIAL VALUES
        # ====================================================

        email_result = None
        url_result = None
        behavior_result = None

        email_score = 0.0
        url_score = 0.0
        behavior_score = 0.0


        # ====================================================
        # EMAIL / BERT
        # ====================================================

        if request.email_text:

            email_result = predict_email(
                request.email_text
            )

            email_score = float(
                email_result.get(
                    "phishing_score",
                    0.0
                )
            )


        # ====================================================
        # URL / CNN
        # ====================================================

        if request.url:

            url_result = predict_url(
                request.url
            )

            url_score = float(
                url_result.get(
                    "url_score",
                    0.0
                )
            )


        # ====================================================
        # BEHAVIOR / ISOLATION FOREST
        # ====================================================

        if request.behavior:

            behavior_result = predict_behavior(
                request.behavior.model_dump()
            )

            behavior_score = float(
                behavior_result.get(
                    "behavior_score",
                    0.0
                )
            )


        # ====================================================
        # DETERMINE ANALYSIS MODE
        # ====================================================

        if request.email_text and request.url:

            mode = "email"

        elif request.url:

            mode = "website"

        else:

            mode = "email"


        # ====================================================
        # FUSION
        # ====================================================

        fusion_result = create_fusion_result(

            email_score=email_score,

            url_score=url_score,

            behavior_score=behavior_score
        )


        # ====================================================
        # RISK SCORING
        # ====================================================

        fusion_result["mode"] = mode

        risk_result = analyze_risk(
            fusion_result
        )


        # ====================================================
        # EXPLANATION
        # ====================================================

        reasons = build_reasons(
            email_result=email_result,
            url_result=url_result,
            behavior_result=behavior_result,
            risk_result=risk_result
        )


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        response = {

            # ------------------------------------------------
            # FINAL RESULT
            # ------------------------------------------------

            "classification":
                risk_result.get(
                    "classification"
                ),

            "risk_score":
                risk_result.get(
                    "risk_score"
                ),

            "risk_percentage":
                risk_result.get(
                    "risk_percentage"
                ),

            "risk_level":
                risk_result.get(
                    "risk_level"
                ),

            "severity":
                risk_result.get(
                    "severity"
                ),

            "confidence":
                risk_result.get(
                    "confidence"
                ),

            "confidence_percentage":
                risk_result.get(
                    "confidence_percentage"
                ),


            # ------------------------------------------------
            # WARNING
            # ------------------------------------------------

            "warning_required":
                risk_result.get(
                    "warning_required"
                ),

            "requires_confirmation":
                risk_result.get(
                    "requires_confirmation"
                ),

            "allow_access":
                risk_result.get(
                    "allow_access"
                ),

            "recommended_action":
                risk_result.get(
                    "recommended_action"
                ),


            # ------------------------------------------------
            # MODEL INFORMATION
            # ------------------------------------------------

            "model_scores":
                get_active_model_scores(
                    risk_result
                ),

            "active_models":
                risk_result.get(
                    "active_models",
                    []
                ),

            "strong_signal_count":
                risk_result.get(
                    "strong_signal_count",
                    0
                ),

            "model_agreement":
                risk_result.get(
                    "model_agreement"
                ),

            "dominant_model":
                risk_result.get(
                    "dominant_model"
                ),

            "dominant_model_score":
                round(
                    float(
                        risk_result.get(
                            "dominant_model_score",
                            0.0
                        )
                    ) * 100,
                    2
                ),


            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            "reasons":
                reasons,


            # ------------------------------------------------
            # RAW MODEL RESULTS
            # ------------------------------------------------

            "models": {

                "email":
                    email_result,

                "url":
                    url_result,

                "behavior":
                    behavior_result
            },


            # ------------------------------------------------
            # FUSION
            # ------------------------------------------------

            "fusion": {

                "fused_score":
                    round(
                        float(
                            fusion_result.get(
                                "fused_score",
                                0.0
                            )
                        ),
                        6
                    ),

                "model_agreement":
                    fusion_result.get(
                        "model_agreement"
                    ),

                "weights":
                    fusion_result.get(
                        "weights"
                    ),

                "contributions":
                    fusion_result.get(
                        "model_contributions",
                        {}
                    )
            },


            # ------------------------------------------------
            # DIAGNOSTICS
            # ------------------------------------------------

            "diagnostic":
                risk_result.get(
                    "diagnostic",
                    {}
                )
        }


        return response


    # ========================================================
    # HTTP ERROR
    # ========================================================

    except HTTPException:

        raise


    # ========================================================
    # VALIDATION ERROR
    # ========================================================

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as exc:

        print(
            "\nANALYSIS ERROR:"
        )

        print(
            repr(exc)
        )

        raise HTTPException(
            status_code=500,
            detail=
                "Phishing analysis failed: "
                + str(exc)
        )