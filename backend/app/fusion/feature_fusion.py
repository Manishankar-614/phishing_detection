from typing import Dict, Optional

import numpy as np


# ============================================================
# DEFAULT MODEL WEIGHTS
# ============================================================

DEFAULT_WEIGHTS = {
    "email": 0.40,
    "url": 0.35,
    "behavior": 0.25,
}


# ============================================================
# SCORE VALIDATION
# ============================================================

def validate_score(
    score: float,
    name: str
) -> float:
    """
    Validate and normalize a model score.

    Every model must return a value between 0 and 1.

    0 = completely legitimate/normal
    1 = completely suspicious/anomalous
    """

    try:
        score = float(score)

    except (TypeError, ValueError):

        raise ValueError(
            f"{name} score must be numeric."
        )

    if not 0.0 <= score <= 1.0:

        raise ValueError(
            f"{name} score must be between 0 and 1."
        )

    return score


# ============================================================
# PREPARE FUSION VECTOR
# ============================================================

def prepare_fusion_input(
    email_score: float,
    url_score: float,
    behavior_score: float
) -> np.ndarray:
    """
    Create the final three-dimensional fusion vector.

    [BERT, CNN, Isolation Forest]
    """

    email_score = validate_score(
        email_score,
        "Email"
    )

    url_score = validate_score(
        url_score,
        "URL"
    )

    behavior_score = validate_score(
        behavior_score,
        "Behavior"
    )

    return np.array(
        [
            email_score,
            url_score,
            behavior_score,
        ],
        dtype=np.float32
    )


# ============================================================
# NORMALIZE WEIGHTS
# ============================================================

def normalize_weights(
    weights: Dict[str, float]
) -> Dict[str, float]:

    required_keys = {
        "email",
        "url",
        "behavior",
    }

    if set(weights.keys()) != required_keys:

        raise ValueError(
            "Weights must contain exactly: "
            "email, url, behavior"
        )

    for key, value in weights.items():

        if value < 0:

            raise ValueError(
                f"Weight for {key} cannot be negative."
            )

    total = sum(
        weights.values()
    )

    if total <= 0:

        raise ValueError(
            "Total weight must be greater than zero."
        )

    return {
        key: value / total
        for key, value in weights.items()
    }


# ============================================================
# WEIGHTED FUSION
# ============================================================

def weighted_fusion(
    email_score: float,
    url_score: float,
    behavior_score: float,
    weights: Optional[
        Dict[str, float]
    ] = None
) -> float:
    """
    Calculate the final fused phishing score.

    Email  = BERT
    URL    = CNN
    Behavior = Isolation Forest
    """

    if weights is None:

        weights = DEFAULT_WEIGHTS.copy()

    weights = normalize_weights(
        weights
    )

    email_score = validate_score(
        email_score,
        "Email"
    )

    url_score = validate_score(
        url_score,
        "URL"
    )

    behavior_score = validate_score(
        behavior_score,
        "Behavior"
    )

    fused_score = (

        email_score
        * weights["email"]

        +

        url_score
        * weights["url"]

        +

        behavior_score
        * weights["behavior"]
    )

    return float(
        np.clip(
            fused_score,
            0.0,
            1.0
        )
    )


# ============================================================
# MODEL AGREEMENT
# ============================================================

def analyze_model_agreement(
    email_score: float,
    url_score: float,
    behavior_score: float
) -> Dict:

    scores = np.array(
        [
            validate_score(
                email_score,
                "Email"
            ),

            validate_score(
                url_score,
                "URL"
            ),

            validate_score(
                behavior_score,
                "Behavior"
            ),
        ],
        dtype=np.float32
    )

    mean_score = float(
        np.mean(scores)
    )

    standard_deviation = float(
        np.std(scores)
    )

    minimum_score = float(
        np.min(scores)
    )

    maximum_score = float(
        np.max(scores)
    )

    score_range = (
        maximum_score
        - minimum_score
    )

    if standard_deviation < 0.15:

        agreement = "high"

    elif standard_deviation < 0.30:

        agreement = "moderate"

    else:

        agreement = "low"

    return {
        "agreement": agreement,
        "mean_score": mean_score,
        "standard_deviation": standard_deviation,
        "minimum_score": minimum_score,
        "maximum_score": maximum_score,
        "score_range": score_range,
    }


# ============================================================
# MODEL CONTRIBUTIONS
# ============================================================

def calculate_contributions(
    email_score: float,
    url_score: float,
    behavior_score: float,
    weights: Optional[
        Dict[str, float]
    ] = None
) -> Dict:

    if weights is None:

        weights = DEFAULT_WEIGHTS.copy()

    weights = normalize_weights(
        weights
    )

    email_score = validate_score(
        email_score,
        "Email"
    )

    url_score = validate_score(
        url_score,
        "URL"
    )

    behavior_score = validate_score(
        behavior_score,
        "Behavior"
    )

    email_contribution = (
        email_score
        * weights["email"]
    )

    url_contribution = (
        url_score
        * weights["url"]
    )

    behavior_contribution = (
        behavior_score
        * weights["behavior"]
    )

    return {
        "email": float(
            email_contribution
        ),

        "url": float(
            url_contribution
        ),

        "behavior": float(
            behavior_contribution
        ),
    }


# ============================================================
# CREATE COMPLETE FUSION RESULT
# ============================================================

def create_fusion_result(
    email_score: float,
    url_score: float,
    behavior_score: float,
    weights: Optional[
        Dict[str, float]
    ] = None
) -> Dict:

    if weights is None:

        weights = DEFAULT_WEIGHTS.copy()

    normalized_weights = normalize_weights(
        weights
    )

    fusion_vector = prepare_fusion_input(
        email_score,
        url_score,
        behavior_score
    )

    fused_score = weighted_fusion(
        email_score,
        url_score,
        behavior_score,
        normalized_weights
    )

    agreement = analyze_model_agreement(
        email_score,
        url_score,
        behavior_score
    )

    contributions = calculate_contributions(
        email_score,
        url_score,
        behavior_score,
        normalized_weights
    )

    return {
        "models": {
            "email": {
                "model": "BERT",
                "score": float(
                    email_score
                ),
                "weight": normalized_weights[
                    "email"
                ],
                "contribution": contributions[
                    "email"
                ],
            },

            "url": {
                "model": "CNN",
                "score": float(
                    url_score
                ),
                "weight": normalized_weights[
                    "url"
                ],
                "contribution": contributions[
                    "url"
                ],
            },

            "behavior": {
                "model": "Isolation Forest",
                "score": float(
                    behavior_score
                ),
                "weight": normalized_weights[
                    "behavior"
                ],
                "contribution": contributions[
                    "behavior"
                ],
            },
        },

        "fusion_vector": (
            fusion_vector.tolist()
        ),

        "fused_score": fused_score,

        "model_agreement": agreement,

        "weights": normalized_weights,
    }


# ============================================================
# TERMINAL INPUT
# ============================================================

def get_score(
    name: str
) -> float:

    while True:

        try:

            value = float(
                input(
                    f"{name} score (0-100%): "
                )
            )

            if not 0 <= value <= 100:

                print(
                    "Enter a value between "
                    "0 and 100."
                )

                continue

            return value / 100

        except ValueError:

            print(
                "Please enter a valid number."
            )


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(
    result: Dict
):

    print("\n" + "=" * 60)
    print("FINAL FUSION RESULT")
    print("=" * 60)

    print("\nModel Scores:")

    for name, model in result[
        "models"
    ].items():

        print(
            f"\n{name.upper()}"
        )

        print(
            f"  Model        : "
            f"{model['model']}"
        )

        print(
            f"  Score        : "
            f"{model['score'] * 100:.2f}%"
        )

        print(
            f"  Weight       : "
            f"{model['weight'] * 100:.2f}%"
        )

        print(
            f"  Contribution : "
            f"{model['contribution'] * 100:.2f}%"
        )

    agreement = result[
        "model_agreement"
    ]

    print(
        "\nModel Agreement:"
    )

    print(
        f"  Level        : "
        f"{agreement['agreement'].upper()}"
    )

    print(
        f"  Mean Score   : "
        f"{agreement['mean_score'] * 100:.2f}%"
    )

    print(
        f"  Std Dev      : "
        f"{agreement['standard_deviation']:.4f}"
    )

    print(
        f"\nFUSED SCORE    : "
        f"{result['fused_score'] * 100:.2f}%"
    )

    print(
        f"\nFusion Vector  : "
        f"{result['fusion_vector']}"
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("FINAL FUSION LAYER")
    print("=" * 60)

    print(
        "\nEnter the outputs from:"
    )

    print(
        "BERT → Email"
    )

    print(
        "CNN → URL"
    )

    print(
        "Isolation Forest → Behavior"
    )

    print("-" * 60)

    email_score = get_score(
        "BERT / Email"
    )

    url_score = get_score(
        "CNN / URL"
    )

    behavior_score = get_score(
        "Isolation Forest / Behavior"
    )

    result = create_fusion_result(
        email_score=email_score,
        url_score=url_score,
        behavior_score=behavior_score,
    )

    display_result(
        result
    )