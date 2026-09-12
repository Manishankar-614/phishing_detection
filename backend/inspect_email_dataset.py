import pandas as pd
from pathlib import Path


DATASET_PATH = Path("datasets/email/email_dataset.csv")


def main():
    print("=" * 60)
    print("EMAIL DATASET INSPECTION")
    print("=" * 60)

    if not DATASET_PATH.exists():
        print(f"\nDataset not found: {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)

    print("\n1. Dataset Shape")
    print("-" * 60)
    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\n2. Column Names")
    print("-" * 60)
    for column in df.columns:
        print(f"- {column}")

    print("\n3. Data Types")
    print("-" * 60)
    print(df.dtypes)

    print("\n4. Missing Values")
    print("-" * 60)
    print(df.isnull().sum())

    print("\n5. Duplicate Rows")
    print("-" * 60)
    print(f"Duplicates: {df.duplicated().sum()}")

    print("\n6. Label Distribution")
    print("-" * 60)

    if "label" in df.columns:
        print(df["label"].value_counts())
        print("\nPercentage:")
        print(df["label"].value_counts(normalize=True).mul(100).round(2))

    print("\n7. Numeric Feature Statistics")
    print("-" * 60)
    print(df.describe().T)

    print("\n8. Email Text Statistics")
    print("-" * 60)

    if "email_text" in df.columns:
        text_lengths = df["email_text"].astype(str).str.len()

        print(f"Average characters : {text_lengths.mean():.2f}")
        print(f"Minimum characters : {text_lengths.min()}")
        print(f"Maximum characters : {text_lengths.max()}")

    print("\n9. Sample Emails")
    print("-" * 60)

    if "email_text" in df.columns and "label" in df.columns:
        for index, row in df.head(5).iterrows():
            print(f"\nSample {index + 1}")
            print(f"Label : {row['label']}")
            print(f"Text  : {str(row['email_text'])[:300]}")

    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()