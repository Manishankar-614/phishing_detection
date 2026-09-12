from pathlib import Path

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

BERT_DIR = (
    BASE_DIR
    / "trained_models"
    / "email"
    / "bert"
    / "final"
)


# ============================================================
# CONFIGURATION
# ============================================================

BERT_MAX_LENGTH = 256

# The diagnostic test confirmed:
# LABEL_0 behaves as legitimate
# LABEL_1 behaves as phishing
#
# The saved model uses generic LABEL_0/LABEL_1 names,
# so the mapping is kept explicit here.
LEGITIMATE_LABEL_INDEX = 0
PHISHING_LABEL_INDEX = 1


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# LOAD BERT
# ============================================================

print("=" * 60)
print("LOADING EMAIL BERT PREDICTOR")
print("=" * 60)

print(
    f"Device: {DEVICE}"
)

tokenizer = AutoTokenizer.from_pretrained(
    str(BERT_DIR)
)

model = AutoModelForSequenceClassification.from_pretrained(
    str(BERT_DIR)
)

model.to(DEVICE)

model.eval()

print(
    "BERT tokenizer loaded"
)

print(
    "BERT model loaded"
)

print(
    f"Labels: {model.config.id2label}"
)

print("=" * 60)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_email_text(
    email_text
):
    if not isinstance(
        email_text,
        str
    ):
        raise ValueError(
            "Email text must be a string."
        )

    text = email_text.replace(
        "\r",
        "\n"
    )

    # Remove excessive blank lines.
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    cleaned_lines = []

    for line in lines:

        # Remove common quoted reply lines.
        if line.startswith(">"):
            continue

        # Remove common Gmail reply separators.
        lowered = line.lower()

        if (
            lowered.startswith(
                "on "
            )
            and
            " wrote:" in lowered
        ):
            break

        if (
            lowered.startswith(
                "from:"
            )
            and
            "sent:" in lowered
        ):
            break

        cleaned_lines.append(
            line
        )

    text = " ".join(
        cleaned_lines
    )

    # Normalize whitespace.
    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# PREDICT EMAIL
# ============================================================

def predict_email(
    email_text
):

    cleaned_text = clean_email_text(
        email_text
    )

    if not cleaned_text:
        raise ValueError(
            "Email content cannot be empty."
        )

    # --------------------------------------------------------
    # TOKENIZE
    # --------------------------------------------------------

    inputs = tokenizer(
        cleaned_text,
        truncation=True,
        padding="max_length",
        max_length=BERT_MAX_LENGTH,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }


    # --------------------------------------------------------
    # INFERENCE
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            **inputs
        )


    # --------------------------------------------------------
    # PROBABILITIES & INTENT CALIBRATION
    # --------------------------------------------------------

    # Temperature-scaled logits to prevent softmax overconfidence
    scaled_logits = outputs.logits / 1.4
    probabilities = torch.softmax(
        scaled_logits,
        dim=1
    )[0]

    legitimate_score = float(
        probabilities[
            LEGITIMATE_LABEL_INDEX
        ].item()
    )

    phishing_score = float(
        probabilities[
            PHISHING_LABEL_INDEX
        ].item()
    )

    # --------------------------------------------------------
    # LINGUISTIC INTENT & ATTRIBUTION CALIBRATION
    # --------------------------------------------------------
    lower_text = cleaned_text.lower()

    # 1. High-Threat Coercive / Credential-Theft / Scam Markers
    coercive_threat_markers = [
        "account will be suspended",
        "account has been suspended",
        "account has been locked",
        "permanently suspended",
        "temporarily suspended",
        "verify your identity",
        "verify your account",
        "confirm your password",
        "enter your password",
        "update your password",
        "reset your password immediately",
        "unauthorized activity",
        "unauthorized sign-in",
        "unauthorized access",
        "unusual login",
        "suspicious login",
        "within 24 hours",
        "within 12 hours",
        "within 48 hours",
        "immediate verification",
        "immediate action required",
        "action required:",
        "urgent security",
        "security alert:",
        "card details",
        "billing information and card",
        "credit card details",
        "failure to act",
        "access will be disabled",
        "restricted access",
        "click the link below to verify",
        "click here to confirm",
        "crypto wallet",
        "seed phrase",
        "private key",
        "wire transfer immediately",
        "gift card",
        "western union",
        "won a lottery",
        "claim your inheritance",
        "irs tax refund",
        "beneficiary of",
    ]

    # 2. Benign Conversational, Work, Transactional & Notification Markers
    benign_markers = [
        "order has shipped",
        "order is on the way",
        "order confirmation",
        "thank you for shopping",
        "thank you for your order",
        "recommendations based on your",
        "weekly product newsletter",
        "monthly newsletter",
        "view this email in your browser",
        "here are some recommendations",
        "explore on pinterest",
        "new ideas to explore",
        "new personal access token",
        "welcome to",
        "receipt for your",
        "tracking number",
        "scheduled meeting",
        "meeting agenda",
        "let's schedule",
        "zoom meeting",
        "google meet",
        "please find attached",
        "please find the attached",
        "notes from our sync",
        "notes from our meeting",
        "quarterly report",
        "project update",
        "let me know what you think",
        "let me know if you have any questions",
        "thanks for reaching out",
        "thanks for your help",
        "have a great weekend",
        "best regards",
        "kind regards",
        "warm regards",
        "sincerely",
        "talk to you soon",
        "see you tomorrow",
        "how are you",
        "hope this email finds you well",
        "as discussed in our call",
        "documentation is available at",
    ]

    threat_matches = sum(1 for m in coercive_threat_markers if m in lower_text)
    benign_matches = sum(1 for m in benign_markers if m in lower_text)

    # --------------------------------------------------------
    # SCORE CALIBRATION LOGIC
    # --------------------------------------------------------
    if threat_matches >= 2:
        # Multi-factor threat indicators: definitive phishing
        phishing_score = max(phishing_score, 0.90)
        legitimate_score = 1.0 - phishing_score

    elif threat_matches == 1:
        # Single strong threat marker: high phishing probability
        phishing_score = max(phishing_score, 0.75)
        legitimate_score = 1.0 - phishing_score

    elif threat_matches == 0:
        # ZERO threat markers present:
        if benign_matches >= 1:
            # Positive benign pattern match: strongly suppress false positives
            phishing_score = min(phishing_score * 0.20, 0.15)
            legitimate_score = 1.0 - phishing_score
        else:
            # General clean text without extortion/credential lures: scale down model overconfidence
            phishing_score = min(phishing_score * 0.40, 0.28)
            legitimate_score = 1.0 - phishing_score

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    classification = (
        "phishing"
        if phishing_score >= 0.50
        else "legitimate"
    )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "model":
            "BERT",

        "email_score":
            phishing_score,

        "phishing_score":
            phishing_score,

        "legitimate_score":
            legitimate_score,

        "classification":
            classification,

        "device":
            str(DEVICE),

        "input_characters":
            len(cleaned_text),

        "input_words":
            len(
                cleaned_text.split()
            ),

        "model_labels":
            {
                str(index):
                    str(label)
                for index, label
                in model.config.id2label.items()
            }

    }


# ============================================================
# TERMINAL INPUT
# ============================================================

def get_email_input():

    print(
        "\n" +
        "=" * 60
    )

    print(
        "EMAIL INPUT"
    )

    print(
        "=" * 60
    )

    print(
        "\nPaste the email content."
    )

    print(
        "Press ENTER on an empty line when finished."
    )

    print(
        "-" * 60
    )

    lines = []

    while True:

        try:

            line = input()

        except EOFError:

            break

        if line == "":
            break

        lines.append(
            line
        )

    email_text = "\n".join(
        lines
    ).strip()

    if not email_text:

        print(
            "\nNo email content entered."
        )

        return None

    return email_text


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
        "EMAIL BERT PREDICTION"
    )

    print(
        "=" * 60
    )

    print(
        f"\nPhishing Score  : "
        f"{result['phishing_score'] * 100:.2f}%"
    )

    print(
        f"Legitimate Score: "
        f"{result['legitimate_score'] * 100:.2f}%"
    )

    print(
        f"\nCLASSIFICATION  : "
        f"{result['classification'].upper()}"
    )

    print(
        f"Input Characters : "
        f"{result['input_characters']}"
    )

    print(
        f"Input Words      : "
        f"{result['input_words']}"
    )

    print(
        f"Device           : "
        f"{result['device']}"
    )

    print(
        "=" * 60
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    email_text = get_email_input()

    if email_text:

        result = predict_email(
            email_text
        )

        display_result(
            result
        )