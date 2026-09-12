import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    matthews_corrcoef,
    confusion_matrix,
)

from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[4]

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "behavior"
    / "behavior_dataset.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "trained_models"
    / "behavior"
    / "isolation_forest"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

FEATURES = [
    "num_clicks",
    "time_on_page",
    "num_redirects",
    "failed_logins",
    "mouse_speed",
    "typing_speed",
    "tab_switches",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset():

    print("=" * 60)
    print("LOADING BEHAVIOR DATASET")
    print("=" * 60)

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nDataset not found:\n"
            f"{DATASET_PATH}"
        )

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"\nTotal records: "
        f"{len(df)}"
    )

    print(
        f"Normal behavior (0): "
        f"{(df['label'] == 0).sum()}"
    )

    print(
        f"Anomalous behavior (1): "
        f"{(df['label'] == 1).sum()}"
    )

    return df


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_dataset(df):

    print("\n" + "=" * 60)
    print("VALIDATING BEHAVIOR DATA")
    print("=" * 60)

    required_columns = FEATURES + [
        "label"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nMissing columns:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )

    if df[required_columns].isnull().any().any():

        raise ValueError(
            "Dataset contains missing values."
        )

    invalid_labels = set(
        df["label"].unique()
    ) - {0, 1}

    if invalid_labels:

        raise ValueError(
            f"Invalid labels found: "
            f"{invalid_labels}"
        )

    print(
        "\nDataset validation successful."
    )

    print(
        f"Behavioral features: "
        f"{len(FEATURES)}"
    )


# ============================================================
# SPLIT DATA
# ============================================================

def split_dataset(df):

    print("\n" + "=" * 60)
    print("SPLITTING BEHAVIOR DATA")
    print("=" * 60)

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_SEED,
        stratify=df["label"]
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_SEED,
        stratify=temp_df["label"]
    )

    print(
        f"\nTraining   : "
        f"{len(train_df)}"
    )

    print(
        f"Validation : "
        f"{len(validation_df)}"
    )

    print(
        f"Testing    : "
        f"{len(test_df)}"
    )

    print("\nTraining distribution:")

    print(
        train_df["label"]
        .value_counts()
        .sort_index()
    )

    print("\nValidation distribution:")

    print(
        validation_df["label"]
        .value_counts()
        .sort_index()
    )

    print("\nTesting distribution:")

    print(
        test_df["label"]
        .value_counts()
        .sort_index()
    )

    return (
        train_df,
        validation_df,
        test_df
    )


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(
    train_df,
    validation_df,
    test_df
):

    print("\n" + "=" * 60)
    print("PREPARING BEHAVIORAL FEATURES")
    print("=" * 60)

    scaler = StandardScaler()

    # --------------------------------------------------------
    # IMPORTANT:
    # Fit scaler ONLY on legitimate training behavior.
    # --------------------------------------------------------

    normal_training_df = train_df[
        train_df["label"] == 0
    ]

    X_normal_train = (
        normal_training_df[
            FEATURES
        ]
        .values
    )

    scaler.fit(
        X_normal_train
    )

    X_train = scaler.transform(
        train_df[FEATURES]
    )

    X_validation = scaler.transform(
        validation_df[FEATURES]
    )

    X_test = scaler.transform(
        test_df[FEATURES]
    )

    print(
        f"\nNormal training samples: "
        f"{len(X_normal_train)}"
    )

    print(
        f"Feature matrix: "
        f"{X_train.shape}"
    )

    return (
        X_train.astype(np.float32),
        X_validation.astype(np.float32),
        X_test.astype(np.float32),
        scaler
    )


# ============================================================
# TRAIN ISOLATION FOREST
# ============================================================

def train_model(
    X_train,
    train_df
):

    print("\n" + "=" * 60)
    print("TRAINING ISOLATION FOREST")
    print("=" * 60)

    # --------------------------------------------------------
    # Only legitimate behavior is used for training.
    # --------------------------------------------------------

    normal_mask = (
        train_df["label"].values == 0
    )

    X_normal = X_train[
        normal_mask
    ]

    print(
        f"\nNormal samples used for training: "
        f"{len(X_normal)}"
    )

    print(
        "Anomalous samples used for training: 0"
    )

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    model = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )

    model.fit(
        X_normal
    )

    print(
        "\nIsolation Forest training complete."
    )

    print(
        f"Trees: "
        f"{model.n_estimators}"
    )

    return model


# ============================================================
# RAW ANOMALY SCORES
# ============================================================

def get_anomaly_scores(
    model,
    X
):

    # Isolation Forest:
    #
    # Higher decision_function =
    # more normal
    #
    # Lower decision_function =
    # more anomalous
    #
    # Therefore we invert the value.

    decision_scores = (
        model.decision_function(X)
    )

    anomaly_scores = -decision_scores

    return anomaly_scores


# ============================================================
# NORMALIZE ANOMALY SCORES
# ============================================================

def normalize_scores(
    scores
):

    minimum = np.min(
        scores
    )

    maximum = np.max(
        scores
    )

    if maximum == minimum:

        return np.zeros_like(
            scores,
            dtype=np.float32
        )

    normalized = (
        scores - minimum
    ) / (
        maximum - minimum
    )

    return normalized.astype(
        np.float32
    )


# ============================================================
# FIND BEST THRESHOLD
# ============================================================

def find_best_threshold(
    validation_scores,
    validation_labels
):

    print("\n" + "=" * 60)
    print("CALIBRATING ANOMALY THRESHOLD")
    print("=" * 60)

    best_threshold = 0.5

    best_f1 = -1

    thresholds = np.linspace(
        0.01,
        0.99,
        199
    )

    for threshold in thresholds:

        predictions = (
            validation_scores
            >= threshold
        ).astype(int)

        score = f1_score(
            validation_labels,
            predictions,
            zero_division=0
        )

        if score > best_f1:

            best_f1 = score
            best_threshold = float(
                threshold
            )

    print(
        f"\nBest threshold: "
        f"{best_threshold:.4f}"
    )

    print(
        f"Validation F1: "
        f"{best_f1 * 100:.2f}%"
    )

    return best_threshold


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(
    test_scores,
    test_labels,
    threshold
):

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    predictions = (
        test_scores
        >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        test_labels,
        predictions
    )

    precision = precision_score(
        test_labels,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        test_labels,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        test_labels,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        test_labels,
        test_scores
    )

    mcc = matthews_corrcoef(
        test_labels,
        predictions
    )

    matrix = confusion_matrix(
        test_labels,
        predictions
    )

    print("\nResults:")

    print(
        f"Accuracy  : "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Precision : "
        f"{precision * 100:.2f}%"
    )

    print(
        f"Recall    : "
        f"{recall * 100:.2f}%"
    )

    print(
        f"F1-Score  : "
        f"{f1 * 100:.2f}%"
    )

    print(
        f"ROC-AUC   : "
        f"{roc_auc * 100:.2f}%"
    )

    print(
        f"MCC       : "
        f"{mcc * 100:.2f}%"
    )

    print("\nConfusion Matrix:")

    print(matrix)

    metrics = {

        "model": "Isolation Forest",

        "accuracy": float(
            accuracy
        ),

        "precision": float(
            precision
        ),

        "recall": float(
            recall
        ),

        "f1_score": float(
            f1
        ),

        "roc_auc": float(
            roc_auc
        ),

        "mcc": float(
            mcc
        ),

        "threshold": float(
            threshold
        )
    }

    return metrics


# ============================================================
# SAVE MODEL
# ============================================================

def save_artifacts(
    model,
    scaler,
    metrics,
    threshold
):

    print("\n" + "=" * 60)
    print("SAVING BEHAVIOR MODEL")
    print("=" * 60)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model_path = (
        MODEL_DIR
        / "isolation_forest.pkl"
    )

    with open(
        model_path,
        "wb"
    ) as file:

        pickle.dump(
            model,
            file
        )

    # --------------------------------------------------------
    # Scaler
    # --------------------------------------------------------

    scaler_path = (
        MODEL_DIR
        / "feature_scaler.pkl"
    )

    with open(
        scaler_path,
        "wb"
    ) as file:

        pickle.dump(
            scaler,
            file
        )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics_path = (
        MODEL_DIR
        / "metrics.json"
    )

    with open(
        metrics_path,
        "w"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    configuration = {

        "model": "Isolation Forest",

        "n_estimators": 300,

        "contamination": "auto",

        "training_strategy":
            "trained_on_legitimate_behavior_only",

        "features": FEATURES,

        "threshold": float(
            threshold
        ),

        "random_seed":
            RANDOM_SEED
    }

    config_path = (
        MODEL_DIR
        / "training_config.json"
    )

    with open(
        config_path,
        "w"
    ) as file:

        json.dump(
            configuration,
            file,
            indent=4
        )

    print(
        f"\nModel saved to:\n"
        f"{model_path}"
    )

    print(
        f"\nScaler saved to:\n"
        f"{scaler_path}"
    )

    print(
        f"\nMetrics saved to:\n"
        f"{metrics_path}"
    )

    print(
        f"\nConfiguration saved to:\n"
        f"{config_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_dataset()

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_dataset(
        df
    )

    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    (
        train_df,
        validation_df,
        test_df
    ) = split_dataset(
        df
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    (
        X_train,
        X_validation,
        X_test,
        scaler
    ) = prepare_features(
        train_df,
        validation_df,
        test_df
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model = train_model(
        X_train,
        train_df
    )

    # --------------------------------------------------------
    # Validation anomaly scores
    # --------------------------------------------------------

    validation_raw_scores = (
        get_anomaly_scores(
            model,
            X_validation
        )
    )

    # Normalize validation scores
    #
    # NOTE:
    # We will save the normalization range later
    # so inference can use the same scale.
    # --------------------------------------------------------

    score_min = float(
        validation_raw_scores.min()
    )

    score_max = float(
        validation_raw_scores.max()
    )

    if score_max == score_min:

        validation_scores = (
            np.zeros_like(
                validation_raw_scores
            )
        )

    else:

        validation_scores = (
            (
                validation_raw_scores
                - score_min
            )
            /
            (
                score_max
                - score_min
            )
        )

    validation_labels = (
        validation_df["label"]
        .values
        .astype(int)
    )

    # --------------------------------------------------------
    # Threshold
    # --------------------------------------------------------

    threshold = find_best_threshold(
        validation_scores,
        validation_labels
    )

    # --------------------------------------------------------
    # Test scores
    # --------------------------------------------------------

    test_raw_scores = (
        get_anomaly_scores(
            model,
            X_test
        )
    )

    if score_max == score_min:

        test_scores = (
            np.zeros_like(
                test_raw_scores
            )
        )

    else:

        test_scores = (
            (
                test_raw_scores
                - score_min
            )
            /
            (
                score_max
                - score_min
            )
        )

        test_scores = np.clip(
            test_scores,
            0.0,
            1.0
        )

    test_labels = (
        test_df["label"]
        .values
        .astype(int)
    )

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    metrics = evaluate_model(
        test_scores,
        test_labels,
        threshold
    )

    # --------------------------------------------------------
    # Save artifacts
    # --------------------------------------------------------

    save_artifacts(
        model,
        scaler,
        metrics,
        threshold
    )

    # --------------------------------------------------------
    # Save score normalization
    # --------------------------------------------------------

    normalization = {

        "score_min":
            score_min,

        "score_max":
            score_max
    }

    normalization_path = (
        MODEL_DIR
        / "score_normalization.json"
    )

    with open(
        normalization_path,
        "w"
    ) as file:

        json.dump(
            normalization,
            file,
            indent=4
        )

    print(
        f"\nScore normalization saved to:\n"
        f"{normalization_path}"
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("ISOLATION FOREST TRAINING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()