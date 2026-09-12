import requests
import json


# ============================================================
# API CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:5000/api/analyze"


# ============================================================
# TEST INPUT
# ============================================================

payload = {

    "email": """
URGENT: Your account requires immediate verification.

Dear Customer,

We detected unusual activity on your account.

Your account will be suspended within 24 hours unless
you verify your identity immediately.

Please click the link below to confirm your account.

Thank you,
Security Team
""",

    "url": "http://secure-account-login.example.tk/verify-account",

    "behavior": {
        "num_clicks": 65,
        "time_on_page": 28.4,
        "num_redirects": 7,
        "failed_logins": 4,
        "mouse_speed": 62.1,
        "typing_speed": 91.4,
        "tab_switches": 12
    }
}


# ============================================================
# SEND REQUEST
# ============================================================

print("=" * 70)
print("PHISHING DETECTION API TEST")
print("=" * 70)

print("\nSending request...")

try:

    response = requests.post(
        API_URL,
        json=payload,
        timeout=300
    )

except requests.exceptions.ConnectionError:

    print(
        "\nERROR: Flask server is not running."
    )

    print(
        "Start it with: python run.py"
    )

    raise SystemExit(1)

except requests.exceptions.Timeout:

    print(
        "\nERROR: Prediction timed out."
    )

    raise SystemExit(1)


# ============================================================
# RESPONSE
# ============================================================

print(
    f"\nHTTP Status: {response.status_code}"
)

print("-" * 70)

try:

    result = response.json()

except ValueError:

    print(
        "Server returned a non-JSON response:"
    )

    print(
        response.text
    )

    raise SystemExit(1)


# ============================================================
# DISPLAY
# ============================================================

print(
    json.dumps(
        result,
        indent=4
    )
)

print("=" * 70)