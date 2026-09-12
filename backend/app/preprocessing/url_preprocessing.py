from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "url"
    / "url_dataset.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "url"
    / "processed"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

REQUIRED_COLUMNS = [
    "url",
    "label",
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
# URL CLEANING
# ============================================================

def clean_url(url):
    """
    Minimal URL cleaning.

    We preserve URL characters because the CNN will learn
    patterns from the original URL structure.
    """

    if pd.isna(url):
        return ""

    return str(url).strip()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("URL DATASET PREPROCESSING")
    print("=" * 60)

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nDataset not found:\n{DATASET_PATH}"
        )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(DATASET_PATH)

    print(
        f"\nOriginal dataset: "
        f"{len(df)} records"
    )

    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "\nMissing required columns:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )

    # Keep only required columns
    df = df[
        REQUIRED_COLUMNS
    ].copy()

    # --------------------------------------------------------
    # Remove duplicate rows
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates()

    print(
        f"Duplicates removed: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # Remove duplicate URLs
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=["url"]
    )

    print(
        f"Duplicate URLs removed: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # Remove missing values
    # --------------------------------------------------------

    before = len(df)

    df = df.dropna(
        subset=REQUIRED_COLUMNS
    )

    print(
        f"Rows with missing values removed: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # Clean URLs
    # --------------------------------------------------------

    df["url"] = df["url"].apply(
        clean_url
    )

    # --------------------------------------------------------
    # Remove empty URLs
    # --------------------------------------------------------

    before = len(df)

    df = df[
        df["url"].str.len() > 0
    ].copy()

    print(
        f"Empty URLs removed: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # Validate labels
    # --------------------------------------------------------

    valid_labels = {0, 1}

    actual_labels = set(
        df["label"].unique()
    )

    if not actual_labels.issubset(
        valid_labels
    ):

        raise ValueError(
            "\nInvalid labels detected: "
            f"{actual_labels}\n"
            "Expected labels: 0 and 1"
        )

    df["label"] = (
        df["label"]
        .astype(int)
    )

    # --------------------------------------------------------
    # Numeric feature conversion
    # --------------------------------------------------------

    numeric_features = [
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

    for feature in numeric_features:

        df[feature] = pd.to_numeric(
            df[feature],
            errors="coerce"
        )

    # Remove rows that became invalid
    before = len(df)

    df = df.dropna(
        subset=numeric_features
    )

    print(
        f"Invalid numeric rows removed: "
        f"{before - len(df)}"
    )

    # --------------------------------------------------------
    # Final dataset information
    # --------------------------------------------------------

    print("\nFinal dataset:")

    print(
        f"Records: {len(df)}"
    )

    print(
        f"Legitimate (0): "
        f"{(df['label'] == 0).sum()}"
    )

    print(
        f"Phishing   (1): "
        f"{(df['label'] == 1).sum()}"
    )

    # --------------------------------------------------------
    # Train / temporary split
    #
    # 80% training
    # 20% temporary
    # --------------------------------------------------------

    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=df["label"]
    )

    # --------------------------------------------------------
    # Validation / test split
    #
    # 10% validation
    # 10% testing
    # --------------------------------------------------------

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_SEED,
        stratify=temp_df["label"]
    )

    # --------------------------------------------------------
    # Print split sizes
    # --------------------------------------------------------

    print("\nDataset split:")

    print(
        f"Training   : "
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

    # --------------------------------------------------------
    # Print label distributions
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save datasets
    # --------------------------------------------------------

    train_path = (
        OUTPUT_DIR
        / "train.csv"
    )

    validation_path = (
        OUTPUT_DIR
        / "validation.csv"
    )

    test_path = (
        OUTPUT_DIR
        / "test.csv"
    )

    train_df.to_csv(
        train_path,
        index=False
    )

    validation_df.to_csv(
        validation_path,
        index=False
    )

    test_df.to_csv(
        test_path,
        index=False
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("\nSaved:")

    print(train_path)
    print(validation_path)
    print(test_path)

    print("\n" + "=" * 60)
    print("URL PREPROCESSING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()