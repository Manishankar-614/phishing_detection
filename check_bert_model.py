from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent

BERT_DIR = (
    PROJECT_DIR
    / "backend"
    / "trained_models"
    / "email"
    / "bert"
    / "final"
)


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 70)
print("BERT MODEL DIAGNOSTIC")
print("=" * 70)

print()
print("Project directory:")
print(PROJECT_DIR)

print()
print("BERT model path:")
print(BERT_DIR)


# ============================================================
# CHECK MODEL PATH
# ============================================================

if not BERT_DIR.exists():

    print()
    print("ERROR: BERT model directory was not found.")

    print()
    print("Expected location:")
    print(BERT_DIR)

    print()
    raise SystemExit(1)


print()
print("BERT model directory found.")


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print()
print("Device:")
print(DEVICE)


# ============================================================
# LOAD TOKENIZER
# ============================================================

print()
print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    str(BERT_DIR)
)

print("Tokenizer loaded successfully.")


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("Loading BERT model...")

model = AutoModelForSequenceClassification.from_pretrained(
    str(BERT_DIR)
)

model.to(DEVICE)

model.eval()

print("BERT model loaded successfully.")


# ============================================================
# MODEL CONFIGURATION
# ============================================================

config = model.config

print()
print("=" * 70)
print("MODEL CONFIGURATION")
print("=" * 70)

print()
print("Number of labels:")
print(config.num_labels)

print()
print("id2label:")
print(config.id2label)

print()
print("label2id:")
print(config.label2id)

print()
print("Problem type:")
print(
    getattr(
        config,
        "problem_type",
        None
    )
)


# ============================================================
# LABEL INTERPRETATION
# ============================================================

print()
print("=" * 70)
print("LABEL INTERPRETATION")
print("=" * 70)

for index in range(config.num_labels):

    label = config.id2label.get(
        index,
        f"UNKNOWN_{index}"
    )

    print(
        f"Index {index}: {label}"
    )


# ============================================================
# DETECT LABEL MEANINGS
# ============================================================

labels = {
    int(index): str(label).lower()
    for index, label
    in config.id2label.items()
}


phishing_index = None
legitimate_index = None


for index, label in labels.items():

    if any(
        word in label
        for word in [
            "phish",
            "malicious",
            "fraud",
            "spam"
        ]
    ):

        phishing_index = index


    if any(
        word in label
        for word in [
            "legit",
            "benign",
            "safe",
            "normal"
        ]
    ):

        legitimate_index = index


print()
print("=" * 70)
print("DETECTED LABEL MAPPING")
print("=" * 70)

print()

if legitimate_index is not None:

    print(
        f"Legitimate label index : "
        f"{legitimate_index}"
    )

else:

    print(
        "Legitimate label index : NOT DETECTED"
    )


if phishing_index is not None:

    print(
        f"Phishing label index   : "
        f"{phishing_index}"
    )

else:

    print(
        "Phishing label index   : NOT DETECTED"
    )


# ============================================================
# CURRENT PREDICTOR ASSUMPTION
# ============================================================

print()
print("=" * 70)
print("CURRENT PROJECT ASSUMPTION")
print("=" * 70)

print()
print("email_predictor.py currently assumes:")

print(
    "Index 0 = legitimate"
)

print(
    "Index 1 = phishing"
)


# ============================================================
# COMPARE MAPPING
# ============================================================

print()
print("=" * 70)
print("ASSUMPTION CHECK")
print("=" * 70)

print()

if (
    legitimate_index == 0
    and phishing_index == 1
):

    print(
        "RESULT: CURRENT LABEL MAPPING IS CORRECT."
    )

    print()
    print(
        "BERT is configured as:"
    )

    print(
        "0 = legitimate"
    )

    print(
        "1 = phishing"
    )


elif (
    legitimate_index == 1
    and phishing_index == 0
):

    print(
        "RESULT: LABEL MAPPING IS REVERSED!"
    )

    print()
    print(
        "The current email_predictor.py "
        "is interpreting BERT incorrectly."
    )

else:

    print(
        "RESULT: LABEL MAPPING NEEDS MANUAL REVIEW."
    )

    print()
    print(
        "The saved model labels could not be "
        "automatically mapped to legitimate/phishing."
    )


# ============================================================
# TEST EMAILS
# ============================================================

test_emails = [

    (
        "LEGITIMATE_TEST",
        """
Hello,

This is a normal notification about your account.

No action is required at this time.

Thank you.
"""
    ),

    (
        "PHISHING_TEST",
        """
URGENT SECURITY ALERT!

Your account will be suspended unless you verify
your account immediately.

Click the link below and enter your password,
verification code, and payment information.

Failure to act within 24 hours will result in
permanent account suspension.
"""
    ),

]


# ============================================================
# BASIC BERT TEST
# ============================================================

print()
print("=" * 70)
print("BASIC BERT PREDICTION TEST")
print("=" * 70)


for test_name, email_text in test_emails:

    inputs = tokenizer(
        email_text,
        truncation=True,
        padding="max_length",
        max_length=256,
        return_tensors="pt"
    )


    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }


    with torch.no_grad():

        outputs = model(
            **inputs
        )


    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )[0]


    print()
    print("-" * 70)

    print(
        f"TEST: {test_name}"
    )

    print()


    for index, probability in enumerate(
        probabilities
    ):

        label = config.id2label.get(
            index,
            f"LABEL_{index}"
        )

        print(
            f"Index {index} "
            f"({label}) : "
            f"{probability.item() * 100:.4f}%"
        )


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 70)
print("BERT DIAGNOSTIC COMPLETE")
print("=" * 70)

print()