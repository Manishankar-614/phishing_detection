from pathlib import Path

import pandas as pd


# ============================================================
# DATASET PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = (
    BASE_DIR
    / "datasets"
    / "behavior"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("BEHAVIOR DATASET INSPECTION")
    print("=" * 60)

    # --------------------------------------------------------
    # Find CSV files
    # --------------------------------------------------------

    csv_files = list(
        DATASET_DIR.glob("*.csv")
    )

    if not csv_files:

        print(
            f"\nNo CSV files found in:\n"
            f"{DATASET_DIR}"
        )

        print(
            "\nPlace the behavior dataset inside:"
        )

        print(
            DATASET_DIR
        )

        return

    print("\nCSV files found:")

    for index, file in enumerate(
        csv_files,
        start=1
    ):

        print(
            f"{index}. {file.name}"
        )

    # --------------------------------------------------------
    # If multiple datasets exist
    # --------------------------------------------------------

    if len(csv_files) > 1:

        print(
            "\nMultiple behavior datasets "
            "were found."
        )

        print(
            "Inspecting the first dataset "
            "for now."
        )

    dataset_path = csv_files[0]

    print(
        f"\nSelected dataset:\n"
        f"{dataset_path}"
    )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(
        dataset_path
    )

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    print("\n1. Dataset Shape")
    print("-" * 60)

    print(
        f"Rows    : {df.shape[0]}"
    )

    print(
        f"Columns : {df.shape[1]}"
    )

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    print("\n2. Column Names")
    print("-" * 60)

    for column in df.columns:

        print(
            f"- {column}"
        )

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\n3. Data Types")
    print("-" * 60)

    print(
        df.dtypes
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\n4. Missing Values")
    print("-" * 60)

    print(
        df.isnull().sum()
    )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    print("\n5. Duplicate Rows")
    print("-" * 60)

    print(
        f"Duplicates: "
        f"{df.duplicated().sum()}"
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    print("\n6. Numeric Columns")
    print("-" * 60)

    numeric_columns = (
        df.select_dtypes(
            include="number"
        ).columns
    )

    for column in numeric_columns:

        print(
            f"- {column}"
        )

    # --------------------------------------------------------
    # Categorical columns
    # --------------------------------------------------------

    print("\n7. Non-Numeric Columns")
    print("-" * 60)

    non_numeric_columns = (
        df.select_dtypes(
            exclude="number"
        ).columns
    )

    for column in non_numeric_columns:

        print(
            f"- {column}"
        )

    # --------------------------------------------------------
    # Numeric statistics
    # --------------------------------------------------------

    if len(numeric_columns) > 0:

        print(
            "\n8. Numeric Feature Statistics"
        )

        print("-" * 60)

        print(
            df[numeric_columns]
            .describe()
            .T
        )

    # --------------------------------------------------------
    # Possible labels
    # --------------------------------------------------------

    print(
        "\n9. Possible Label Columns"
    )

    print("-" * 60)

    possible_labels = [
        "label",
        "target",
        "class",
        "is_phishing",
        "is_anomaly",
        "anomaly"
    ]

    found_labels = []

    for column in df.columns:

        if column.lower() in possible_labels:

            found_labels.append(
                column
            )

    if found_labels:

        for column in found_labels:

            print(
                f"\nColumn: {column}"
            )

            print(
                df[column]
                .value_counts(
                    dropna=False
                )
            )

    else:

        print(
            "No obvious label column found."
        )

    # --------------------------------------------------------
    # Sample records
    # --------------------------------------------------------

    print("\n10. Sample Records")
    print("-" * 60)

    print(
        df.head(10).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("INSPECTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()