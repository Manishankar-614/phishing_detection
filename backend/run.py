import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.api.routes import api


def create_app():
    # ============================================================
    # CREATE FLASK APP
    # ============================================================
    app = Flask(__name__)

    # ============================================================
    # CORS CONFIGURATION
    # ============================================================
    cors_origins = os.environ.get("CORS_ORIGINS", "*")
    if cors_origins != "*":
        cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=True,
    )

    # ============================================================
    # REGISTER BLUEPRINTS
    # ============================================================
    app.register_blueprint(api)

    # ============================================================
    # ROOT & HEALTH CHECK ENDPOINTS
    # ============================================================
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "name": "PhishGuard AI Detection API",
            "version": "2.0.0",
            "status": "online",
            "models": {
                "email": "BERT (Transformer)",
                "url": "Deep Character-level CNN",
                "behavior": "Isolation Forest (Anomaly Detection)"
            },
            "pipeline": [
                "Email Preprocessing & BERT Scoring",
                "URL Feature Extraction & CNN Scoring",
                "Behavioral Anomaly Detection",
                "Dynamic Feature Fusion",
                "Multi-Tier Risk Assessment",
                "Explainability & Attribution Engine"
            ]
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "PhishGuard AI Backend",
            "environment": os.environ.get("FLASK_ENV", "production")
        }), 200

    return app


app = create_app()


# ============================================================
# RUN SERVER (LOCAL & PRODUCTION ENTRYPOINT)
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

    print(f"Starting PhishGuard AI API on {host}:{port} (debug={debug})")
    app.run(
        host=host,
        port=port,
        debug=debug
    )