from flask import Flask
from flask_cors import CORS

from app.api.routes import api


# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(
    __name__
)


# ============================================================
# CORS
# ============================================================

CORS(
    app
)


# ============================================================
# REGISTER API
# ============================================================

app.register_blueprint(
    api
)


# ============================================================
# ROOT
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return {
        "name": "Hybrid Phishing Detection API",
        "status": "running",
        "models": {
            "email": "BERT",
            "url": "CNN",
            "behavior": "Isolation Forest"
        },
        "pipeline": [
            "BERT",
            "CNN",
            "Isolation Forest",
            "Feature Fusion",
            "Risk Scoring",
            "Explainability"
        ]
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )