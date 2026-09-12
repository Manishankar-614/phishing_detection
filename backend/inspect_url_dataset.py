from pathlib import Path

import pandas as pd


# ============================================================
# PATH
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent
    / "datasets"
    / "url"
    / "url_dataset.csv"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("URL DATASET INSPECTION")
    print("=" * 60)

    if not DATASET_PATH.exists():

        print(
            f"\nDataset not found:\n{DATASET_PATH}"
        )

        return

    df = pd.read_csv(DATASET_PATH)

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    print("\n1. Dataset Shape")
    print("-" * 60)

    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    print("\n2. Column Names")
    print("-" * 60)

    for column in df.columns:
        print(f"- {column}")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\n3. Data Types")
    print("-" * 60)

    print(df.dtypes)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\n4. Missing Values")
    print("-" * 60)

    print(df.isnull().sum())

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    print("\n5. Duplicate Rows")
    print("-" * 60)

    print(
        f"Duplicates: {df.duplicated().sum()}"
    )

    # --------------------------------------------------------
    # Duplicate URLs
    # --------------------------------------------------------

    if "url" in df.columns:

        print("\n6. Duplicate URLs")
        print("-" * 60)

        print(
            f"Duplicate URLs: "
            f"{df['url'].duplicated().sum()}"
        )

    # --------------------------------------------------------
    # Label distribution
    # --------------------------------------------------------

    if "label" in df.columns:

        print("\n7. Label Distribution")
        print("-" * 60)

        print(
            df["label"].value_counts()
        )

        print("\nPercentage:")

        print(
            df["label"]
            .value_counts(normalize=True)
            .mul(100)
            .round(2)
        )

    # --------------------------------------------------------
    # Numeric statistics
    # --------------------------------------------------------

    print("\n8. Numeric Feature Statistics")
    print("-" * 60)

    print(
        df.describe().T
    )

    # --------------------------------------------------------
    # URL length
    # --------------------------------------------------------

    if "url" in df.columns:

        print("\n9. URL Length Statistics")
        print("-" * 60)

        url_lengths = (
            df["url"]
            .astype(str)
            .str.len()
        )

        print(
            f"Average length : "
            f"{url_lengths.mean():.2f}"
        )

        print(
            f"Minimum length : "
            f"{url_lengths.min()}"
        )

        print(
            f"Maximum length : "
            f"{url_lengths.max()}"
        )

    # --------------------------------------------------------
    # Sample URLs
    # --------------------------------------------------------

    print("\n10. Sample URLs")
    print("-" * 60)

    if "url" in df.columns and "label" in df.columns:

        for index, row in df.head(10).iterrows():

            print(
                f"\nSample {index + 1}"
            )

            print(
                f"Label : {row['label']}"
            )

            print(
                f"URL   : {row['url']}"
            )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()