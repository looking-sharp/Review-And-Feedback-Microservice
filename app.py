from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import datetime
import uuid
import json 

app = Flask(__name__)

# CORS Configuration
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": [o.strip() for o in allowed_origins if o.strip()],
        "methods": ["GET", "POST", "PUT", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Mock Database
# Olivia: Replace MOCK_DB with a real database connection 
MOCK_DB = {}

def error_response(message, code=400):
    return jsonify({"error": message}), code

#  Database Helper Functions
def get_feedback(feedbackId):
    """
    Olivia: Replace MOCK_DB lookup with actual DB query. 
    """
    return MOCK_DB.get(feedbackId)


def save_feedback(userId, entityId, rating, comment):
    """
    Olivia: Replace MOCK_DB insertion with actual DB insert logic. 
    """
    feedbackId = str(uuid.uuid4())
    MOCK_DB[feedbackId] = {
        "feedbackId": feedbackId,
        "userId": userId,
        "entityId": entityId,
        "rating": rating,
        "comment": comment,
        "last_modified": datetime.datetime.utcnow().isoformat()
    }
    return feedbackId


def update_feedback_entry(feedbackId, rating, comment, last_modified):
    """
    Olivia: Replace MOCK_DB update with actual DB UPDATE logic.
    """
    if feedbackId in MOCK_DB:
        MOCK_DB[feedbackId]["rating"] = rating
        MOCK_DB[feedbackId]["comment"] = comment
        MOCK_DB[feedbackId]["last_modified"] = last_modified.isoformat()
        return True
    return False


def log_audit(audit_log):
    """
    Olivia: Replace print statement with actual audit logging mechanism if needed. 
    """
    print(f"AUDIT_LOG_ENTRY: {json.dumps(audit_log)}")

#  Routes
@app.route("/health")
def health():
    return jsonify({"message": "Review and Feedback Microservice Online"}), 200


@app.route("/feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()
    except Exception:
        return error_response("Invalid JSON format")

    if not data:
        return error_response("No data provided")

    userId = data.get("userId")
    entityId = data.get("entityId")
    rating = data.get("rating")
    comment = data.get("comment")

    # Validation
    if not all([userId, entityId, rating]):
        return error_response("Missing required fields (userId, entityId, rating)")

    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return error_response("Rating must be an integer between 1 and 5")

    feedbackId = save_feedback(userId, entityId, rating, comment)

    return jsonify({
        "message": "Feedback received",
        "feedbackId": feedbackId,
        "userId": userId,
        "entityId": entityId,
        "rating": rating,
        "comment": comment
    }), 201


@app.route("/feedback/<feedbackId>", methods=["PUT"])
def update_feedback_endpoint(feedbackId):
    try:
        data = request.get_json()
    except Exception:
        return error_response("Invalid JSON format")

    if not data:
        return error_response("No data provided")

    userId = data.get("userId")
    rating = data.get("rating")
    comment = data.get("comment")

    # Validation
    if rating is not None:
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return error_response("Rating must be an integer between 1 and 5")

    if comment is not None and not isinstance(comment, str):
        return error_response("Comment must be a string")


    original_feedback = get_feedback(feedbackId)

    if not original_feedback:
        return error_response("Feedback not found", 404)

    if original_feedback.get("userId") != userId:
        return error_response("Unauthorized", 403)

    # Audit log
    print(f"AUDIT: Feedback {feedbackId} updated by user {userId}")

    update_feedback_entry(feedbackId, rating, comment, datetime.datetime.utcnow())

    return jsonify({
        "message": "Feedback updated",
        "feedbackId": feedbackId,
        "changes": {"rating": rating, "comment": comment}
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5005"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
