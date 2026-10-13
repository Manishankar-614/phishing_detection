from flask import Blueprint, jsonify, request

from app.predictors.master_predictor import analyze_input
from app.feedback.feedback_manager import feedback_manager


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
        # RECORD SCAN IN EXTENSION HISTORY
        # ========================================================
        try:
            feedback_manager.record_scan(
                email_text=email_text,
                url=url,
                result=result,
                source="Web Portal & Extension Hook"
            )
        except Exception as record_err:
            print(f"Warning: could not record scan in history: {record_err}")

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


# ============================================================
# EXTENSION ADMIN CONTROL PANEL ENDPOINTS
# ============================================================

@api.route("/admin/stats", methods=["GET"])
def get_admin_stats():
    """Returns real-time aggregate statistics for the extension control panel."""
    try:
        stats = feedback_manager.get_stats()
        return jsonify({
            "status": "success",
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve stats: {str(e)}"
        }), 500


@api.route("/admin/scans", methods=["GET"])
def get_admin_scans():
    """Returns filtered, searchable scan logs for the extension control panel."""
    try:
        filter_type = request.args.get("filter", "all")
        search = request.args.get("search", "")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        data = feedback_manager.get_scans(
            filter_type=filter_type,
            search=search,
            limit=limit,
            offset=offset
        )
        return jsonify({
            "status": "success",
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve scans: {str(e)}"
        }), 500


@api.route("/admin/correct", methods=["POST"])
def submit_admin_correction():
    """Submits human-in-the-loop correction and updates active calibration."""
    try:
        data = request.get_json(silent=True) or {}
        scan_id = data.get("scan_id", "")
        corrected_label = data.get("corrected_label", "").lower().strip()
        reason = data.get("reason", "")
        admin_name = data.get("admin", "Administrator")

        if corrected_label not in ("legitimate", "phishing"):
            return jsonify({
                "status": "error",
                "message": "corrected_label must be either 'legitimate' or 'phishing'."
            }), 400

        result = feedback_manager.submit_correction(
            scan_id=scan_id,
            corrected_label=corrected_label,
            reason=reason,
            admin_name=admin_name
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to submit correction: {str(e)}"
        }), 500


@api.route("/admin/retrain", methods=["POST"])
def trigger_admin_retrain():
    """Triggers adaptive self-retraining cycle over all feedback samples."""
    try:
        result = feedback_manager.trigger_retraining()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to execute retraining: {str(e)}"
        }), 500


@api.route("/admin/policies", methods=["GET"])
def get_admin_policies():
    """Returns active domain and pattern policies."""
    try:
        policies = feedback_manager.get_policies()
        return jsonify({
            "status": "success",
            "data": policies
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch policies: {str(e)}"
        }), 500


@api.route("/admin/policies", methods=["POST"])
def add_admin_policy():
    """Adds a domain override policy directly from the SOC control panel."""
    try:
        data = request.get_json(silent=True) or {}
        domain = data.get("domain", "").strip()
        classification = data.get("classification", "legitimate").strip().lower()
        reason = data.get("reason", "Added via SOC Policy Manager")

        if not domain:
            return jsonify({"status": "error", "message": "Domain is required."}), 400
        if classification not in ("legitimate", "phishing"):
            return jsonify({"status": "error", "message": "Classification must be 'legitimate' or 'phishing'."}), 400

        updated = feedback_manager.add_domain_policy(domain, classification, reason)
        return jsonify({
            "status": "success",
            "message": f"Policy for '{domain}' saved as {classification.upper()}.",
            "data": updated
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to add policy: {str(e)}"
        }), 500


@api.route("/admin/policies", methods=["DELETE"])
def delete_admin_policy():
    """Removes a domain policy from active calibration memory."""
    try:
        data = request.get_json(silent=True) or {}
        domain = data.get("domain", "").strip()
        if not domain:
            return jsonify({"status": "error", "message": "Domain is required."}), 400

        updated = feedback_manager.delete_domain_policy(domain)
        return jsonify({
            "status": "success",
            "message": f"Policy for '{domain}' removed.",
            "data": updated
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to delete policy: {str(e)}"
        }), 500


@api.route("/admin/benchmark", methods=["GET"])
def get_admin_benchmark():
    """Returns scientific validation benchmark performance metrics and confusion matrix."""
    try:
        benchmark = feedback_manager.get_benchmark_metrics()
        return jsonify(benchmark)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to compute benchmark metrics: {str(e)}"
        }), 500
