from pathlib import Path
import pickle
import re

import numpy as np
import pandas as pd
import tensorflow as tf


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "trained_models"
    / "url"
    / "cnn"
)

MODEL_PATH = (
    MODEL_DIR
    / "url_cnn_model.keras"
)

VOCAB_PATH = (
    MODEL_DIR
    / "char_to_index.pkl"
)

SCALER_PATH = (
    MODEL_DIR
    / "feature_scaler.pkl"
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_URL_LENGTH = 256

URL_FEATURES = [
    "url_length",
    "digit_ratio",
    "special_char_ratio",
    "entropy_score",
    "suspicious_keyword_count",
    "path_depth",
    "subdomain_count",
    "tld_risk_score",
    "https_flag",
    "domain_length",
    "number_of_dots",
    "number_of_hyphens",
]


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("LOADING URL PREDICTION MODEL")
print("=" * 60)

url_model = tf.keras.models.load_model(
    MODEL_PATH
)

with open(
    VOCAB_PATH,
    "rb"
) as file:
    char_to_index = pickle.load(file)

with open(
    SCALER_PATH,
    "rb"
) as file:
    feature_scaler = pickle.load(file)

print("URL CNN loaded")
print("Character vocabulary loaded")
print("Feature scaler loaded")

print("=" * 60)


# ============================================================
# ENCODE URL
# ============================================================

def encode_url(url):

    encoded = np.zeros(
        (
            1,
            MAX_URL_LENGTH
        ),
        dtype=np.int32
    )

    url = str(url).strip()

    url = url[:MAX_URL_LENGTH]

    for index, character in enumerate(url):

        encoded[
            0,
            index
        ] = char_to_index.get(
            character,
            0
        )

    return encoded


# ============================================================
# ENTROPY
# ============================================================

def calculate_entropy(value):

    if not value:
        return 0.0

    characters, counts = np.unique(
        list(value),
        return_counts=True
    )

    probabilities = (
        counts / counts.sum()
    )

    entropy = -np.sum(
        probabilities
        * np.log2(
            probabilities
        )
    )

    return float(entropy)


# ============================================================
# SUSPICIOUS KEYWORDS
# ============================================================

def count_suspicious_keywords(url):

    keywords = [
        "login",
        "signin",
        "verify",
        "verification",
        "account",
        "update",
        "secure",
        "security",
        "password",
        "confirm",
        "bank",
        "wallet",
        "payment",
        "paypal",
        "credential",
        "authorize",
        "authentication",
    ]

    url_lower = url.lower()

    return sum(
        1
        for keyword in keywords
        if keyword in url_lower
    )


# ============================================================
# URL FEATURES
# ============================================================

def extract_url_features(url):

    url = str(url).strip()

    url_length = len(url)

    digit_count = sum(
        character.isdigit()
        for character in url
    )

    digit_ratio = (
        digit_count / url_length
        if url_length > 0
        else 0.0
    )

    special_character_count = sum(
        not character.isalnum()
        for character in url
    )

    special_char_ratio = (
        special_character_count / url_length
        if url_length > 0
        else 0.0
    )

    entropy_score = calculate_entropy(
        url
    )

    suspicious_keyword_count = (
        count_suspicious_keywords(
            url
        )
    )

    path_depth = url.count("/")

    domain = (
        url.split(
            "://",
            1
        )[-1]
        .split(
            "/",
            1
        )[0]
    )

    domain_without_port = (
        domain.split(
            ":",
            1
        )[0]
    )

    domain_parts = [
        part
        for part in domain_without_port.split(".")
        if part
    ]

    subdomain_count = max(
        len(domain_parts) - 2,
        0
    )

    domain_length = len(
        domain_without_port
    )

    risky_tlds = {
        ".tk",
        ".ml",
        ".ga",
        ".cf",
        ".gq",
        ".top",
        ".xyz",
        ".click",
        ".zip",
        ".mov",
    }

    url_lower = url.lower()

    tld_risk_score = int(
        any(
            url_lower.endswith(tld)
            or f"{tld}/" in url_lower
            or f"{tld}?" in url_lower
            for tld in risky_tlds
        )
    )

    https_flag = int(
        url_lower.startswith(
            "https://"
        )
    )

    number_of_dots = url.count(".")

    number_of_hyphens = url.count("-")

    return pd.DataFrame(
        [[
            url_length,
            digit_ratio,
            special_char_ratio,
            entropy_score,
            suspicious_keyword_count,
            path_depth,
            subdomain_count,
            tld_risk_score,
            https_flag,
            domain_length,
            number_of_dots,
            number_of_hyphens,
        ]],
        columns=URL_FEATURES
    )


# ============================================================
# PREDICT URL
# ============================================================

def predict_url(url):

    if not isinstance(url, str):
        raise ValueError(
            "URL must be a string."
        )

    if not url.strip():
        raise ValueError(
            "URL cannot be empty."
        )

    encoded_url = encode_url(
        url
    )

    features = extract_url_features(
        url
    )

    scaled_features = (
        feature_scaler.transform(
            features
        )
    )

    scaled_features = (
        scaled_features.astype(
            np.float32
        )
    )

    probability = (
        url_model.predict(
            {
                "url_input": encoded_url,
                "url_features": scaled_features,
            },
            verbose=0
        )[0][0]
    )

    probability = float(
        probability
    )

    # --------------------------------------------------------
    # STRUCTURAL CALIBRATION (REDUCE FP & FN)
    # --------------------------------------------------------
    domain_part = (
        url.split("://", 1)[-1]
        .split("/", 1)[0]
        .split(":", 1)[0]
        .strip()
    )

    # 1. Direct IPv4 host detection (e.g. http://124.6.185.122/bin.sh) -> Strong indicator
    is_ipv4_host = bool(
        re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain_part)
    )
    if is_ipv4_host:
        probability = max(probability, 0.85)

    # 2. Deceptive multi-level subdomain depth (>= 4 dots in host)
    elif domain_part.count(".") >= 4:
        probability = max(probability, 0.70)

    classification = (
        "phishing"
        if probability >= 0.50
        else "legitimate"
    )

    return {
        "model": "url_cnn",
        "url_score": probability,
        "classification": classification,
        "features": {
            column: float(
                features.iloc[0][column]
            )
            for column in URL_FEATURES
        },
    }


# ============================================================
# TERMINAL INPUT
# ============================================================

def get_url_input():

    print("\n" + "=" * 60)
    print("URL INPUT")
    print("=" * 60)

    url = input(
        "\nEnter URL: "
    ).strip()

    if not url:

        print(
            "\nNo URL entered."
        )

        return None

    return url


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    print("\n" + "=" * 60)
    print("URL PREDICTION RESULT")
    print("=" * 60)

    print(
        f"\nURL Score      : "
        f"{result['url_score'] * 100:.2f}%"
    )

    print(
        f"CLASSIFICATION : "
        f"{result['classification'].upper()}"
    )

    print("\nExtracted Features:")

    for key, value in result[
        "features"
    ].items():

        print(
            f"{key:28}: {value}"
        )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    url = get_url_input()

    if url:

        result = predict_url(
            url
        )

        display_result(
            result
        )