from flask import Blueprint, jsonify, request

from app.predictors.master_predictor import analyze_input


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


# ============================================================
# HEALTH CHECK
# ============================================================

@api.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "success",
        "message": "Phishing Detection API is running"
    })


# ============================================================
# COMPLETE PHISHING ANALYSIS
# ============================================================

@api.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({
                "status": "error",
                "message": "Request body must contain JSON."
            }), 400


        email_text = (
            data.get("email") or ""
        ).strip()


        url = (
            data.get("url") or ""
        ).strip()


        email_urls = data.get(
            "email_urls",
            []
        )


        email_links = data.get(
            "email_links",
            []
        )


        behavior = data.get(
            "behavior"
        )


        is_email_page = bool(
            data.get(
                "is_email_page",
                False
            )
        )


        # ========================================================
        # VALIDATE BEHAVIOR
        # ========================================================

        if not isinstance(
            behavior,
            dict
        ):

            return jsonify({
                "status": "error",
                "message": "Behavior must be an object."
            }), 400


        # ========================================================
        # VALIDATE ANALYSIS MODE
        # ========================================================

        if is_email_page:

            # ----------------------------------------------------
            # Email mode
            # ----------------------------------------------------

            if not email_text:

                return jsonify({
                    "status": "error",
                    "message": "Email content is required."
                }), 400


            # URL is optional for email.
            # Some emails have no links.


        else:

            # ----------------------------------------------------
            # Website mode
            # ----------------------------------------------------

            if not url:

                return jsonify({
                    "status": "error",
                    "message": "URL is required."
                }), 400


        # ========================================================
        # RUN PIPELINE
        # ========================================================

        result = analyze_input(

            email_text=email_text,

            url=url,

            behavior_data=behavior,

            is_email_page=is_email_page,

            email_urls=email_urls,

            email_links=email_links

        )


        # ========================================================
        # RESPONSE
        # ========================================================

        return jsonify({

            "status": "success",

            "result": result

        })


    except ValueError as error:

        return jsonify({

            "status": "error",

            "message": str(error)

        }), 400


    except Exception as error:

        print(
            f"API ERROR: {error}"
        )


        return jsonify({

            "status": "error",

            "message": "Internal prediction error."

        }), 500