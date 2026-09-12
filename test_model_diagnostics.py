import json
import requests

API_URL = "http://127.0.0.1:5000/api/analyze"

BASE_BEHAVIOR = {
    "num_clicks": 0,
    "time_on_page": 5,
    "num_redirects": 0,
    "failed_logins": 0,
    "mouse_speed": 0,
    "typing_speed": 0,
    "tab_switches": 0
}

TESTS = [
    {
        "name": "LEGITIMATE - Amazon style",
        "email": """Your Amazon order has shipped.

Hello,
Your recent order is on the way. You can review your order status and delivery details from your Amazon account.

Thank you for shopping with us.""",
        "email_links": [
            {
                "text": "View your order",
                "url": "https://www.amazon.com/gp/css/order-history"
            }
        ]
    },
    {
        "name": "LEGITIMATE - Pinterest style",
        "email": """You have new ideas to explore on Pinterest.

Here are some recommendations based on your recent activity. Open Pinterest to see more ideas and save the ones you like.

Thanks,
Pinterest""",
        "email_links": [
            {
                "text": "Open Pinterest",
                "url": "https://www.pinterest.com/"
            }
        ]
    },
    {
        "name": "LEGITIMATE - Generic newsletter",
        "email": """Weekly product newsletter

Here are this week's updates, articles, and product news. Read the latest edition when you have time.

You can unsubscribe from future newsletters using the link below.""",
        "email_links": [
            {
                "text": "View online",
                "url": "https://example.com/newsletter"
            },
            {
                "text": "Unsubscribe",
                "url": "https://example.com/unsubscribe"
            }
        ]
    },
    {
        "name": "PHISHING - Credential theft",
        "email": """URGENT: Your account will be suspended today.

We detected unusual activity. Verify your account immediately to prevent permanent suspension.

Confirm your account now or your access will be disabled within 24 hours.""",
        "email_links": [
            {
                "text": "Verify your account",
                "url": "http://secure-account-verification.example.xyz/login/confirm"
            }
        ]
    },
    {
        "name": "PHISHING - Payment",
        "email": """Immediate payment verification required.

Your payment could not be completed. Confirm your billing information and card details immediately to avoid cancellation.

Failure to verify may result in account restrictions.""",
        "email_links": [
            {
                "text": "Confirm payment",
                "url": "http://billing-security.example.top/verify/payment"
            }
        ]
    }
]


def score(value):
    try:
        return float(value or 0.0) * 100
    except (TypeError, ValueError):
        return 0.0


def run_test(test):
    payload = {
        "email": test["email"],
        "url": "https://mail.google.com/",
        "page_url": "https://mail.google.com/",
        "title": test["name"],
        "is_email_page": True,
        "email_urls": [
            item["url"]
            for item in test["email_links"]
        ],
        "email_links": test["email_links"],
        "behavior": BASE_BEHAVIOR
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    result = response.json()

    email = result.get("email", {})
    url = result.get("url", {})
    behavior = result.get("behavior", {})
    fusion = result.get("fusion", {})
    risk = result.get("risk", {})
    explanation = result.get("explanation", {})

    print("\n" + "=" * 80)
    print(test["name"])
    print("=" * 80)
    print(f"BERT / Email          : {score(email.get('email_score')):7.2f}%")
    print(f"CNN / URL             : {score(url.get('url_score')):7.2f}%")
    print(f"Isolation Forest      : {score(behavior.get('behavior_score')):7.2f}%")
    print(f"Fusion                : {score(fusion.get('fused_score')):7.2f}%")
    print(f"Final risk            : {score(risk.get('risk_score')):7.2f}%")
    print(f"Classification        : {risk.get('classification')}")
    print(f"Agreement             : {risk.get('model_agreement')}")
    print(f"Dominant model        : {risk.get('dominant_model')}")
    print(f"Contributions         : {risk.get('model_contributions', {})}")

    print("\nReasons:")
    for reason in explanation.get("reasons", [])[:10]:
        if isinstance(reason, dict):
            print(
                f"- [{reason.get('severity', 'low')}] "
                f"{reason.get('source', 'unknown')}: "
                f"{reason.get('reason', '')}"
            )
        else:
            print(f"- {reason}")

    return result


if __name__ == "__main__":
    print("Phishing Detection AI - Model Diagnostic Test")
    print(f"API: {API_URL}")
    print("\nThis test does not whitelist any domain.")
    print("Every sample is passed through the normal BERT/CNN/Isolation Forest pipeline.")

    for test in TESTS:
        try:
            run_test(test)
        except Exception as error:
            print(f"\n{test['name']} FAILED: {error}")