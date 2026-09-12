from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# Paths
BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "datasets" / "email" / "email_dataset.csv"
OUTPUT_DIR = BASE_DIR / "datasets" / "email" / "processed"


def clean_text(text):
    """Basic text normalization."""
    if pd.isna(text):
        return ""

    text = str(text)
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")
    text = " ".join(text.split())

    return text


def main():
    print("=" * 60)
    print("EMAIL DATASET PREPROCESSING")
    print("=" * 60)

    # Load dataset
    df = pd.read_csv(DATASET_PATH)

    print(f"\nOriginal dataset: {len(df)} records")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f"Duplicates removed: {before - len(df)}")

    # Remove rows with missing required values
    before = len(df)
    df = df.dropna(subset=["email_text", "label"])
    print(f"Rows with missing email/label removed: {before - len(df)}")

    # Clean email text
    df["email_text"] = df["email_text"].apply(clean_text)

    # Remove empty emails
    before = len(df)
    df = df[df["email_text"].str.len() > 0].copy()
    print(f"Empty emails removed: {before - len(df)}")

    # Validate labels
    valid_labels = {0, 1}

    if not set(df["label"].unique()).issubset(valid_labels):
        raise ValueError("Dataset contains labels other than 0 and 1.")

    df["label"] = df["label"].astype(int)

    print("\nFinal dataset:")
    print(f"Records: {len(df)}")
    print(f"Legitimate (0): {(df['label'] == 0).sum()}")
    print(f"Phishing   (1): {(df['label'] == 1).sum()}")

    # First split: 80% train, 20% temporary
    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,
        random_state=42,
        stratify=df["label"]
    )

    # Second split: temporary → 10% validation + 10% test
    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["label"]
    )

    print("\nDataset split:")
    print(f"Training   : {len(train_df)}")
    print(f"Validation : {len(validation_df)}")
    print(f"Testing    : {len(test_df)}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save processed datasets
    train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
    validation_df.to_csv(OUTPUT_DIR / "validation.csv", index=False)
    test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

    print("\nSaved:")
    print(OUTPUT_DIR / "train.csv")
    print(OUTPUT_DIR / "validation.csv")
    print(OUTPUT_DIR / "test.csv")

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()