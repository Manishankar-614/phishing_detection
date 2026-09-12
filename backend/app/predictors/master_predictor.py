from pathlib import Path
import re
import sys
import numpy as np


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]


if str(BASE_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(BASE_DIR)
    )


# ============================================================
# IMPORT PREDICTORS
# ============================================================

from app.predictors.email_predictor import (
    predict_email
)

from app.predictors.url_predictor import (
    predict_url
)

from app.predictors.behavior_predictor import (
    predict_behavior
)

from app.risk.risk_scoring import (
    analyze_risk
)

from app.explainability.explainability_engine import (
    generate_explanation
)


# ============================================================
# SAFE SCORE
# ============================================================

def safe_score(
    value
):

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return 0.0


    return max(
        0.0,
        min(
            1.0,
            value
        )
    )


# ============================================================
# SINGLE URL ANALYSIS
# ============================================================

def analyze_single_url(
    url
):

    if not url:

        return {

            "model":
                "CNN",

            "url_score":
                0.0,

            "classification":
                "not_analyzed",

            "features":
                {},

            "url":
                ""

        }


    result = predict_url(
        url
    )


    if not isinstance(
        result,
        dict
    ):

        result = {}


    result["model"] = (
        result.get(
            "model",
            "CNN"
        )
    )


    result["url"] = url


    result["url_score"] = safe_score(
        result.get(
            "url_score",
            0.0
        )
    )


    return result


# ============================================================
# AUXILIARY EMAIL LINK DETECTION
# ============================================================

def is_auxiliary_email_link(
    link
):

    if not isinstance(
        link,
        dict
    ):

        return False


    text = (
        link.get(
            "text",
            ""
        )
        or ""
    ).lower().strip()


    url = (
        link.get(
            "url",
            ""
        )
        or ""
    ).lower()


    auxiliary_text = [

        "unsubscribe",

        "manage preferences",

        "email preferences",

        "email preference",

        "opt out",

        "opt-out",

        "view in browser",

        "view online",

        "privacy policy",

        "terms of service",

        "terms & conditions",

        "terms and conditions",

    ]


    for word in auxiliary_text:

        if word in text:

            return True


    auxiliary_url_parts = [

        "/unsubscribe",

        "/unsub",

        "/preferences",

        "/email-preferences",

        "/optout",

        "/opt-out",

        "/view-in-browser",

        "/viewonline",

        "/privacy-policy",

        "/terms",

    ]


    for part in auxiliary_url_parts:

        if part in url:

            return True


    return False


# ============================================================
# EMAIL URL ANALYSIS
# ============================================================

def analyze_email_urls(
    email_urls=None,
    email_links=None
):

    if email_urls is None:
        email_urls = []


    if email_links is None:
        email_links = []


    candidates = []


    # --------------------------------------------------------
    # STRUCTURED LINKS
    # --------------------------------------------------------

    if isinstance(
        email_links,
        list
    ):

        for link in email_links:

            if not isinstance(
                link,
                dict
            ):

                continue


            link_url = (
                link.get(
                    "url",
                    ""
                )
                or ""
            ).strip()


            if not link_url:
                continue


            if not link_url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                continue


            candidates.append({

                "url":
                    link_url,

                "text":
                    (
                        link.get(
                            "text",
                            ""
                        )
                        or ""
                    ).strip(),

                "auxiliary":
                    is_auxiliary_email_link(
                        link
                    )

            })


    # --------------------------------------------------------
    # FALLBACK URL LIST
    # --------------------------------------------------------

    if (
        not candidates
        and
        isinstance(
            email_urls,
            list
        )
    ):

        for link_url in email_urls:

            if not isinstance(
                link_url,
                str
            ):

                continue


            link_url = (
                link_url.strip()
            )


            if not link_url:
                continue


            if not link_url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                continue


            candidates.append({

                "url":
                    link_url,

                "text":
                    "",

                "auxiliary":
                    False

            })


    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    unique_candidates = []

    seen = set()


    for item in candidates:

        link_url = item[
            "url"
        ]


        if link_url in seen:

            continue


        seen.add(
            link_url
        )

        unique_candidates.append(
            item
        )


    # Don't send an unlimited number of URLs
    # to the CNN.

    candidates = (
        unique_candidates[:10]
    )


    # --------------------------------------------------------
    # ANALYZE URLs
    # --------------------------------------------------------

    results = []


    for item in candidates:

        try:

            prediction = (
                analyze_single_url(
                    item["url"]
                )
            )


            results.append({

                "url":
                    item["url"],

                "text":
                    item["text"],

                "auxiliary":
                    item["auxiliary"],

                "score":
                    safe_score(
                        prediction.get(
                            "url_score",
                            0.0
                        )
                    ),

                "classification":
                    prediction.get(
                        "classification",
                        "unknown"
                    ),

                "features":
                    prediction.get(
                        "features",
                        {}
                    )

            })


        except Exception as error:

            results.append({

                "url":
                    item["url"],

                "text":
                    item["text"],

                "auxiliary":
                    item["auxiliary"],

                "score":
                    0.0,

                "classification":
                    "analysis_error",

                "features":
                    {},

                "error":
                    str(error)

            })


    # --------------------------------------------------------
    # MEANINGFUL LINKS
    # --------------------------------------------------------

    meaningful_links = [

        item

        for item in results

        if not item.get(
            "auxiliary",
            False
        )

    ]


    # --------------------------------------------------------
    # URL SCORE
    #
    # Instead of letting one URL determine the entire
    # email URL score, use the strongest few meaningful
    # URLs and average them.
    # --------------------------------------------------------

    if meaningful_links:

        sorted_links = sorted(

            meaningful_links,

            key=lambda item:
                item.get(
                    "score",
                    0.0
                ),

            reverse=True

        )


        top_links = (
            sorted_links[:3]
        )


        url_score = (

            sum(
                item.get(
                    "score",
                    0.0
                )
                for item
                in top_links
            )
            /
            len(top_links)

        )


    else:

        url_score = 0.0


    url_score = safe_score(
        url_score
    )


    # --------------------------------------------------------
    # PRIMARY URL
    # --------------------------------------------------------

    primary_url = ""


    if meaningful_links:

        primary_url = max(

            meaningful_links,

            key=lambda item:
                item.get(
                    "score",
                    0.0
                )

        ).get(
            "url",
            ""
        )


    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    if not meaningful_links:

        url_classification = (
            "not_analyzed"
        )

    elif url_score >= 0.50:

        url_classification = (
            "phishing"
        )

    else:

        url_classification = (
            "legitimate"
        )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "model":
            "CNN",

        "urls_found":
            len(results),

        "meaningful_urls":
            len(
                meaningful_links
            ),

        "auxiliary_urls":
            (
                len(results)
                -
                len(
                    meaningful_links
                )
            ),

        "primary_url":
            primary_url,

        "url_score":
            url_score,

        "classification":
            url_classification,

        "links":
            results

    }


# ============================================================
# MODEL AGREEMENT
# ============================================================

def calculate_model_agreement(
    scores
):

    if not scores:

        return {

            "agreement":
                "unknown",

            "maximum_score":
                0.0,

            "mean_score":
                0.0,

            "minimum_score":
                0.0,

            "score_range":
                0.0,

            "standard_deviation":
                0.0

        }


    scores = [

        safe_score(
            score
        )

        for score
        in scores

    ]


    maximum = max(
        scores
    )

    minimum = min(
        scores
    )

    mean = (
        sum(scores)
        /
        len(scores)
    )


    variance = (

        sum(
            (
                score - mean
            ) ** 2

            for score
            in scores
        )

        /

        len(scores)

    )


    standard_deviation = (
        variance ** 0.5
    )


    score_range = (
        maximum - minimum
    )


    if score_range < 0.15:

        agreement = "high"

    elif score_range < 0.30:

        agreement = "medium"

    else:

        agreement = "low"


    return {

        "agreement":
            agreement,

        "maximum_score":
            float(maximum),

        "mean_score":
            float(mean),

        "minimum_score":
            float(minimum),

        "score_range":
            float(score_range),

        "standard_deviation":
            float(
                standard_deviation
            )

    }


# ============================================================
# EMAIL FUSION
# ============================================================

def create_email_fusion(
    email_score,
    url_score,
    behavior_score,
    has_meaningful_url
):

    email_score = safe_score(
        email_score
    )

    url_score = safe_score(
        url_score
    )

    behavior_score = safe_score(
        behavior_score
    )


    # ========================================================
    # IMPORTANT
    #
    # Isolation Forest is an anomaly detector, not a
    # calibrated phishing classifier.
    #
    # Therefore it receives a small contribution.
    # ========================================================

    if has_meaningful_url:

        email_weight = 0.55

        url_weight = 0.40

        behavior_weight = 0.05

        fused_score = (
            email_score * email_weight
            + url_score * url_weight
            + behavior_score * behavior_weight
        )

        # ----------------------------------------------------
        # ANTI-FALSE-NEGATIVE: DOMINANT MALICIOUS LINK
        # A dangerous URL must not be diluted by clean email text
        # ----------------------------------------------------
        if url_score >= 0.75:
            fused_score = max(fused_score, url_score * 0.90, 0.75)

        elif email_score >= 0.85 and url_score >= 0.50:
            fused_score = max(fused_score, 0.80)

        # ----------------------------------------------------
        # ANTI-FALSE-POSITIVE: CLEAN TRANSACTIONAL EMAIL
        # Clean URLs + moderate email score should not trigger false alarm
        # ----------------------------------------------------
        elif url_score < 0.15 and email_score < 0.65:
            fused_score = min(fused_score, 0.30)

        scores = [
            email_score,
            url_score,
            behavior_score
        ]

        weights = {
            "email": email_weight,
            "url": url_weight,
            "behavior": behavior_weight
        }

    else:

        email_weight = 0.90

        behavior_weight = 0.10

        fused_score = (
            email_score * email_weight
            + behavior_score * behavior_weight
        )

        scores = [
            email_score,
            behavior_score
        ]

        weights = {
            "email": email_weight,
            "url": 0.0,
            "behavior": behavior_weight
        }


    # --------------------------------------------------------
    # MODEL AGREEMENT
    # --------------------------------------------------------

    model_agreement = (
        calculate_model_agreement(
            scores
        )
    )


    # --------------------------------------------------------
    # DOMINANT MODEL
    # --------------------------------------------------------

    model_values = {
        "email": email_score,
        "url": url_score,
        "behavior": behavior_score
    }

    dominant_model = max(
        model_values,
        key=model_values.get
    )


    # --------------------------------------------------------
    # CONTRIBUTIONS
    # --------------------------------------------------------

    contributions = {
        name: safe_score(
            model_values[name] * weights.get(name, 0.0)
        )
        for name in model_values
    }


    # --------------------------------------------------------
    # FUSION RESULT
    # --------------------------------------------------------

    return {
        "fused_score": safe_score(fused_score),
        "fusion_vector": scores,
        "weights": weights,
        "models": {
            "email": {
                "score": email_score,
                "classification": (
                    "phishing"
                    if email_score >= 0.50
                    else "legitimate"
                )
            },
            "url": {
                "score": url_score,
                "classification": (
                    "phishing"
                    if url_score >= 0.50
                    else "legitimate"
                )
            },
            "behavior": {
                "score": behavior_score,
                "classification": (
                    "anomalous"
                    if behavior_score >= 0.50
                    else "normal"
                )
            }
        },
        "model_agreement": model_agreement,
        "dominant_model": dominant_model,
        "mode": "email"
    }


# ============================================================
# WEBSITE FUSION
# ============================================================

def create_website_fusion(
    url_score,
    behavior_score
):

    url_score = safe_score(
        url_score
    )

    behavior_score = safe_score(
        behavior_score
    )

    url_weight = 0.85

    behavior_weight = 0.15

    fused_score = (
        url_score * url_weight
        + behavior_score * behavior_weight
    )

    # If the URL is definitively dangerous, prevent behavior from diluting it
    if url_score >= 0.75:
        fused_score = max(fused_score, url_score)

    # If URL is clearly benign and no high-risk anomaly, dampen false positives
    elif url_score < 0.20 and behavior_score < 0.70:
        fused_score = min(fused_score, 0.30)

    scores = [
        url_score,
        behavior_score
    ]


    return {

        "fused_score":
            safe_score(
                fused_score
            ),

        "fusion_vector":
            scores,

        "weights": {

            "email":
                0.0,

            "url":
                url_weight,

            "behavior":
                behavior_weight

        },

        "models": {

            "email": {

                "score":
                    0.0,

                "classification":
                    "not_analyzed"

            },

            "url": {

                "score":
                    url_score,

                "classification":
                    (
                        "phishing"
                        if url_score >= 0.50
                        else "legitimate"
                    )

            },

            "behavior": {

                "score":
                    behavior_score,

                "classification":
                    (
                        "anomalous"
                        if behavior_score >= 0.50
                        else "normal"
                    )

            }

        },

        "model_agreement":
            calculate_model_agreement(
                scores
            ),

        "dominant_model":
            (
                "url"
                if url_score >= behavior_score
                else "behavior"
            ),

        "mode":
            "website"

    }


# ============================================================
# EXPLANATION
# ============================================================

def generate_final_explanation(
    email_score,
    url_score,
    behavior_score,
    url_features,
    behavior_features,
    model_agreement,
    mode
):

    explanation = generate_explanation(

        email_score=email_score,

        url_score=url_score,

        behavior_score=behavior_score,

        url_features=url_features,

        behavior_features=behavior_features,

        model_agreement=model_agreement

    )


    if not isinstance(
        explanation,
        dict
    ):

        explanation = {

            "summary":
                "",

            "reasons":
                []

        }


    if not isinstance(
        explanation.get(
            "reasons"
        ),
        list
    ):

        explanation[
            "reasons"
        ] = []


    if mode == "email":

        explanation[
            "summary"
        ] = (

            "Email analysis completed using "
            "BERT for email content, CNN for "
            "meaningful email URLs, and Isolation "
            "Forest for behavioural anomaly detection."

        )

    else:

        explanation[
            "summary"
        ] = (

            "Website analysis completed using "
            "CNN for URL analysis and Isolation "
            "Forest for behavioural anomaly detection."

        )


    return explanation


# ============================================================
# MASTER PREDICTOR
# ============================================================

def analyze_input(
    email_text: str,
    url: str,
    behavior_data: dict,
    is_email_page: bool = False,
    email_urls=None,
    email_links=None
):

    if email_urls is None:
        email_urls = []

    if email_links is None:
        email_links = []

    if not isinstance(
        behavior_data,
        dict
    ):
        raise ValueError(
            "Behavior data must be an object."
        )

    email_text = (email_text or "").strip()
    url = (url or "").strip()

    # Extract embedded URLs from email body
    extracted_urls = re.findall(r"https?://[^\s<>\"'\)]+", email_text) if email_text else []

    # Merge explicit URL and body links
    merged_email_urls = list(email_urls)
    if url and url not in merged_email_urls:
        merged_email_urls.append(url)
    for ext_u in extracted_urls:
        if ext_u not in merged_email_urls:
            merged_email_urls.append(ext_u)

    # ========================================================
    # EMAIL / HYBRID MODE
    # ========================================================

    if is_email_page or email_text:

        if not email_text:
            raise ValueError(
                "Email content is required."
            )

        # ----------------------------------------------------
        # BERT
        # ----------------------------------------------------

        email_result = predict_email(
            email_text
        )

        if not isinstance(
            email_result,
            dict
        ):
            email_result = {}

        email_score = safe_score(
            email_result.get(
                "email_score",
                0.0
            )
        )

        # ----------------------------------------------------
        # CNN URL
        # ----------------------------------------------------

        email_url_result = (
            analyze_email_urls(
                email_urls=merged_email_urls,
                email_links=email_links
            )
        )


        url_score = safe_score(
            email_url_result.get(
                "url_score",
                0.0
            )
        )


        # ----------------------------------------------------
        # BEHAVIOR
        # ----------------------------------------------------

        behavior_result = predict_behavior(
            behavior_data
        )


        if not isinstance(
            behavior_result,
            dict
        ):

            behavior_result = {}


        behavior_score = safe_score(
            behavior_result.get(
                "behavior_score",
                0.0
            )
        )


        # ----------------------------------------------------
        # FUSION
        # ----------------------------------------------------

        has_meaningful_url = (

            email_url_result.get(
                "meaningful_urls",
                0
            )
            >
            0

        )


        fusion_result = create_email_fusion(

            email_score=
                email_score,

            url_score=
                url_score,

            behavior_score=
                behavior_score,

            has_meaningful_url=
                has_meaningful_url

        )


        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        risk_result = analyze_risk(
            fusion_result
        )


        # ----------------------------------------------------
        # URL FEATURES
        # ----------------------------------------------------

        url_features = {}

        links = email_url_result.get(
            "links",
            []
        )


        if links:

            primary_link = max(

                links,

                key=lambda item:
                    item.get(
                        "score",
                        0.0
                    )

            )


            url_features = (
                primary_link.get(
                    "features",
                    {}
                )
            )


        # ----------------------------------------------------
        # BEHAVIOR FEATURES
        # ----------------------------------------------------

        behavior_features = (
            behavior_result.get(
                "features",
                {}
            )
        )


        # ----------------------------------------------------
        # EXPLANATION
        # ----------------------------------------------------

        explanation_result = (
            generate_final_explanation(

                email_score=
                    email_score,

                url_score=
                    url_score,

                behavior_score=
                    behavior_score,

                url_features=
                    url_features,

                behavior_features=
                    behavior_features,

                model_agreement=
                    fusion_result[
                        "model_agreement"
                    ],

                mode=
                    "email"

            )
        )


        # ----------------------------------------------------
        # AUXILIARY INFORMATION
        # ----------------------------------------------------

        auxiliary_count = (
            email_url_result.get(
                "auxiliary_urls",
                0
            )
        )


        if auxiliary_count > 0:

            explanation_result[
                "reasons"
            ].append({

                "reason": (

                    f"{auxiliary_count} auxiliary, "
                    "unsubscribe, preference, or "
                    "tracking-style link(s) were not "
                    "used as the primary URL signal."

                ),

                "severity":
                    "low",

                "source":
                    "url"

            })


        # ----------------------------------------------------
        # FINAL EMAIL RESULT
        # ----------------------------------------------------

        return {

            "mode":
                "email",

            "email":
                email_result,

            "url": {

                "model":
                    "CNN",

                "url_score":
                    url_score,

                "classification":
                    email_url_result.get(
                        "classification",
                        "not_analyzed"
                    ),

                "primary_url":
                    email_url_result.get(
                        "primary_url",
                        ""
                    ),

                "urls_found":
                    email_url_result.get(
                        "urls_found",
                        0
                    ),

                "meaningful_urls":
                    email_url_result.get(
                        "meaningful_urls",
                        0
                    ),

                "auxiliary_urls":
                    email_url_result.get(
                        "auxiliary_urls",
                        0
                    ),

                "links":
                    email_url_result.get(
                        "links",
                        []
                    )

            },

            "behavior":
                behavior_result,

            "fusion":
                fusion_result,

            "risk":
                risk_result,

            "model_results": {

                "bert": {

                    "score":
                        email_score,

                    "classification":
                        email_result.get(
                            "classification",
                            "unknown"
                        )

                },

                "cnn": {

                    "score":
                        url_score,

                    "classification":
                        email_url_result.get(
                            "classification",
                            "not_analyzed"
                        )

                },

                "isolation_forest": {

                    "score":
                        behavior_score,

                    "classification":
                        behavior_result.get(
                            "classification",
                            "unknown"
                        )

                },

                "model_agreement":
                    fusion_result[
                        "model_agreement"
                    ],

                "dominant_model":
                    fusion_result[
                        "dominant_model"
                    ]

            },

            "explanation":
                explanation_result

        }


    # ========================================================
    # WEBSITE MODE
    # ========================================================

    url = (
        url or ""
    ).strip()


    if not url:

        raise ValueError(
            "URL is required."
        )


    # --------------------------------------------------------
    # CNN
    # --------------------------------------------------------

    url_result = analyze_single_url(
        url
    )


    url_score = safe_score(
        url_result.get(
            "url_score",
            0.0
        )
    )


    # --------------------------------------------------------
    # BEHAVIOR
    # --------------------------------------------------------

    behavior_result = predict_behavior(
        behavior_data
    )


    if not isinstance(
        behavior_result,
        dict
    ):

        behavior_result = {}


    behavior_score = safe_score(
        behavior_result.get(
            "behavior_score",
            0.0
        )
    )


    # --------------------------------------------------------
    # FUSION
    # --------------------------------------------------------

    fusion_result = create_website_fusion(

        url_score=
            url_score,

        behavior_score=
            behavior_score

    )


    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk_result = analyze_risk(
        fusion_result
    )


    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    explanation_result = (
        generate_final_explanation(

            email_score=0.0,

            url_score=url_score,

            behavior_score=behavior_score,

            url_features=
                url_result.get(
                    "features",
                    {}
                ),

            behavior_features=
                behavior_result.get(
                    "features",
                    {}
                ),

            model_agreement=
                fusion_result[
                    "model_agreement"
                ],

            mode="website"

        )
    )


    # --------------------------------------------------------
    # FINAL WEBSITE RESULT
    # --------------------------------------------------------

    return {

        "mode":
            "website",

        "email": {

            "model":
                "BERT",

            "email_score":
                0.0,

            "classification":
                "not_analyzed"

        },

        "url":
            url_result,

        "behavior":
            behavior_result,

        "fusion":
            fusion_result,

        "risk":
            risk_result,

        "model_results": {

            "bert": {

                "score":
                    0.0,

                "classification":
                    "not_analyzed"

            },

            "cnn": {

                "score":
                    url_score,

                "classification":
                    url_result.get(
                        "classification",
                        "unknown"
                    )

            },

            "isolation_forest": {

                "score":
                    behavior_score,

                "classification":
                    behavior_result.get(
                        "classification",
                        "unknown"
                    )

            },

            "model_agreement":
                fusion_result[
                    "model_agreement"
                ],

            "dominant_model":
                fusion_result[
                    "dominant_model"
                ]

        },

        "explanation":
            explanation_result

    }


# ============================================================
# TERMINAL DISPLAY
# ============================================================

def display_final_result(
    result
):

    print(
        "\n" +
        "=" * 70
    )

    print(
        "FINAL PHISHING DETECTION RESULT"
    )

    print(
        "=" * 70
    )


    print(
        "\nMODEL RESULTS"
    )

    print(
        "-" * 70
    )


    print(
        f"BERT / Email       : "
        f"{result['email']['email_score'] * 100:.2f}%"
    )


    print(
        f"CNN / URL          : "
        f"{result['url']['url_score'] * 100:.2f}%"
    )


    print(
        f"Isolation Forest    : "
        f"{result['behavior']['behavior_score'] * 100:.2f}%"
    )


    print(
        "\nFUSION"
    )

    print(
        "-" * 70
    )


    print(
        f"Fused Score        : "
        f"{result['fusion']['fused_score'] * 100:.2f}%"
    )


    agreement = (
        result[
            "fusion"
        ][
            "model_agreement"
        ]
    )


    print(
        f"Agreement          : "
        f"{agreement['agreement'].upper()}"
    )


    print(
        f"Dominant Model     : "
        f"{result['fusion']['dominant_model']}"
    )


    print(
        "\nRISK ASSESSMENT"
    )

    print(
        "-" * 70
    )


    risk = result[
        "risk"
    ]


    print(
        f"Risk Score         : "
        f"{risk['risk_percentage']:.2f}%"
    )


    print(
        f"Risk Level         : "
        f"{risk['risk_level'].upper()}"
    )


    print(
        f"Classification     : "
        f"{risk['classification'].upper()}"
    )


    print(
        f"Confidence         : "
        f"{risk['confidence_percentage']:.2f}%"
    )


    print(
        f"Recommended Action : "
        f"{risk['recommended_action']}"
    )


    print(
        "\n" +
        "=" * 70
    )


# ============================================================
# TERMINAL INPUT
# ============================================================

def get_email():

    print(
        "\n" +
        "=" * 70
    )

    print(
        "EMAIL"
    )

    print(
        "=" * 70
    )

    print(
        "Paste email content."
    )

    print(
        "Press ENTER on an empty line when finished."
    )

    print(
        "-" * 70
    )


    lines = []


    while True:

        line = input()


        if line == "":
            break


        lines.append(
            line
        )


    return "\n".join(
        lines
    ).strip()


def get_url():

    print(
        "\n" +
        "=" * 70
    )

    print(
        "URL"
    )

    print(
        "=" * 70
    )


    return input(
        "Enter URL: "
    ).strip()


def get_behavior():

    print(
        "\n" +
        "=" * 70
    )

    print(
        "BEHAVIOR"
    )

    print(
        "=" * 70
    )


    behavior = {}


    behavior[
        "num_clicks"
    ] = float(
        input(
            "Number of clicks: "
        )
    )


    behavior[
        "time_on_page"
    ] = float(
        input(
            "Time on page (seconds): "
        )
    )


    behavior[
        "num_redirects"
    ] = float(
        input(
            "Number of redirects: "
        )
    )


    behavior[
        "failed_logins"
    ] = float(
        input(
            "Failed logins: "
        )
    )


    behavior[
        "mouse_speed"
    ] = float(
        input(
            "Mouse speed: "
        )
    )


    behavior[
        "typing_speed"
    ] = float(
        input(
            "Typing speed: "
        )
    )


    behavior[
        "tab_switches"
    ] = float(
        input(
            "Tab switches: "
        )
    )


    return behavior


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n" +
        "=" * 70
    )

    print(
        "HYBRID PHISHING DETECTION SYSTEM"
    )

    print(
        "=" * 70
    )


    email_text = get_email()


    if not email_text:

        print(
            "\nEmail cannot be empty."
        )

        sys.exit(1)


    url = get_url()


    if not url:

        print(
            "\nURL cannot be empty."
        )

        sys.exit(1)


    behavior_data = get_behavior()


    result = analyze_input(

        email_text=
            email_text,

        url=
            url,

        behavior_data=
            behavior_data

    )


    display_final_result(
        result
    )