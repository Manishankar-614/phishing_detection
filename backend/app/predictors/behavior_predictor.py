from pathlib import Path

import json
import pickle

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "trained_models"
    / "behavior"
    / "isolation_forest"
)

MODEL_PATH = (
    MODEL_DIR
    / "isolation_forest.pkl"
)

SCALER_PATH = (
    MODEL_DIR
    / "feature_scaler.pkl"
)

NORMALIZATION_PATH = (
    MODEL_DIR
    / "score_normalization.json"
)

CONFIG_PATH = (
    MODEL_DIR
    / "training_config.json"
)


# ============================================================
# FEATURES
# ============================================================

BEHAVIOR_FEATURES = [

    "num_clicks",

    "time_on_page",

    "num_redirects",

    "failed_logins",

    "mouse_speed",

    "typing_speed",

    "tab_switches",

]


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("LOADING BEHAVIOR PREDICTION MODEL")
print("=" * 60)

with open(
    MODEL_PATH,
    "rb"
) as file:

    behavior_model = pickle.load(
        file
    )


with open(
    SCALER_PATH,
    "rb"
) as file:

    behavior_scaler = pickle.load(
        file
    )


with open(
    NORMALIZATION_PATH,
    "r"
) as file:

    normalization = json.load(
        file
    )


with open(
    CONFIG_PATH,
    "r"
) as file:

    training_config = json.load(
        file
    )


SCORE_MIN = float(
    normalization[
        "score_min"
    ]
)

SCORE_MAX = float(
    normalization[
        "score_max"
    ]
)

THRESHOLD = float(
    training_config[
        "threshold"
    ]
)


print(
    "Isolation Forest loaded"
)

print(
    "Behavior scaler loaded"
)

print(
    "Score normalization loaded"
)

print(
    f"Calibrated threshold: "
    f"{THRESHOLD:.4f}"
)

print("=" * 60)


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_number(
    value,
    default=0.0
):

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return default

    if not np.isfinite(
        value
    ):

        return default

    return value


# ============================================================
# PREDICT BEHAVIOR
# ============================================================

def predict_behavior(
    behavior_data
):

    if not isinstance(
        behavior_data,
        dict
    ):

        raise ValueError(
            "behavior_data must be a dictionary."
        )


    missing_features = [

        feature

        for feature
        in BEHAVIOR_FEATURES

        if feature not in behavior_data

    ]


    if missing_features:

        raise ValueError(
            "Missing behavior features: "
            +
            ", ".join(
                missing_features
            )
        )


    # --------------------------------------------------------
    # BUILD FEATURE FRAME
    # --------------------------------------------------------

    features = pd.DataFrame(
        [[
            safe_number(
                behavior_data[
                    feature
                ]
            )

            for feature
            in BEHAVIOR_FEATURES
        ]],
        columns=BEHAVIOR_FEATURES
    )


    # --------------------------------------------------------
    # SCALE
    # --------------------------------------------------------

    scaled_features = (
        behavior_scaler.transform(
            features
        )
    )


    # --------------------------------------------------------
    # ISOLATION FOREST
    # --------------------------------------------------------

    decision_score = float(
        behavior_model
        .decision_function(
            scaled_features
        )[0]
    )


    raw_anomaly_score = (
        -decision_score
    )


    # --------------------------------------------------------
    # NORMALIZE ANOMALY SCORE
    # --------------------------------------------------------

    if SCORE_MAX == SCORE_MIN:

        anomaly_score = 0.0

    else:

        anomaly_score = (

            raw_anomaly_score
            -
            SCORE_MIN

        ) / (

            SCORE_MAX
            -
            SCORE_MIN

        )


        anomaly_score = float(
            np.clip(
                anomaly_score,
                0.0,
                1.0
            )
        )


    # --------------------------------------------------------
    # ANOMALY CLASSIFICATION
    # --------------------------------------------------------

    classification = (

        "anomalous"

        if anomaly_score >= THRESHOLD

        else "normal"

    )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "model":
            "isolation_forest",

        "behavior_score":
            anomaly_score,

        "anomaly_score":
            anomaly_score,

        "raw_anomaly_score":
            raw_anomaly_score,

        "decision_score":
            decision_score,

        "threshold":
            THRESHOLD,

        "classification":
            classification,

        "signal_type":
            "behavioral_anomaly",

        "features": {

            feature:
                float(
                    features.iloc[
                        0
                    ][feature]
                )

            for feature
            in BEHAVIOR_FEATURES

        }

    }


# ============================================================
# TERMINAL INPUT
# ============================================================

def get_behavior_input():

    print(
        "\n" +
        "=" * 60
    )

    print(
        "BEHAVIOR INPUT"
    )

    print(
        "=" * 60
    )

    behavior_data = {}

    descriptions = {

        "num_clicks":
            "Number of clicks",

        "time_on_page":
            "Time on page (seconds)",

        "num_redirects":
            "Number of redirects",

        "failed_logins":
            "Failed login attempts",

        "mouse_speed":
            "Mouse speed",

        "typing_speed":
            "Typing speed",

        "tab_switches":
            "Number of tab switches",

    }


    for feature in BEHAVIOR_FEATURES:

        while True:

            try:

                value = float(
                    input(
                        f"{descriptions[feature]}: "
                    )
                )

                if value < 0:

                    print(
                        "Value cannot be negative."
                    )

                    continue

                behavior_data[
                    feature
                ] = value

                break

            except ValueError:

                print(
                    "Please enter a valid number."
                )


    return behavior_data


# ============================================================
# DISPLAY
# ============================================================

def display_result(
    result
):

    print(
        "\n" +
        "=" * 60
    )

    print(
        "BEHAVIOR PREDICTION RESULT"
    )

    print(
        "=" * 60
    )

    print(
        f"\nAnomaly Score : "
        f"{result['behavior_score'] * 100:.2f}%"
    )

    print(
        f"Raw Anomaly   : "
        f"{result['raw_anomaly_score']:.6f}"
    )

    print(
        f"Threshold     : "
        f"{result['threshold'] * 100:.2f}%"
    )

    print(
        f"CLASSIFICATION: "
        f"{result['classification'].upper()}"
    )

    print(
        "\nInput Features:"
    )

    for key, value in result[
        "features"
    ].items():

        print(
            f"{key:20}: {value}"
        )

    print(
        "=" * 60
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    behavior_data = get_behavior_input()

    result = predict_behavior(
        behavior_data
    )

    display_result(
        result
    )