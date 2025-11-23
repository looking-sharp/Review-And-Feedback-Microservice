from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone
import os
import uuid
import json
import requests

app = Flask(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")

# Authentication Integration
# This function verifies the JWT token by calling the /auth/verify endpoint
# of the User Authentication Microservice. If valid, it returns the user info
# (id, email, name) to be used for all feedback operations.
def verify_token(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/auth/verify", headers={"Authorization": f"Bearer {token}"})
        if resp.status_code == 200:
            return resp.json()["user"]  # contains id, email, name
    except Exception:
        pass
    return None

# CORS Configuration
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": [o.strip() for o in allowed_origins if o.strip()],
        "methods": ["GET", "POST", "PUT", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["review_feedback_db"]
feedback_collection = db["feedbacks"]
audit_collection = db["audit_logs"]

# Audit Logging Integration
# This function sends audit log entries to the centralized Audit and Logging Microservice
# via HTTP POST to the /log endpoint. This replaces direct MongoDB writes for audit logs.
AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:5001")

def error_response(message, code=400):
    return jsonify({"error": message}), code

#  Database Helper Functions
def get_feedback(feedbackId):
    feedback = feedback_collection.find_one({"feedbackId": feedbackId})
    if feedback:
        feedback.pop("_id", None)
    
    return feedback

def save_feedback(userId, entityId, rating, comment):
    feedbackId = str(uuid.uuid4())
    feedback_doc = {
        "feedbackId": feedbackId,
        "userId": userId,
        "entityId": entityId,
        "rating": rating,
        "comment": comment,
        "last_modified": datetime.now(timezone.utc).isoformat()
    }
    feedback_collection.insert_one(feedback_doc)
    
    return feedbackId


def update_feedback_entry(feedbackId, rating, comment, last_modified):
    update_data = {
        "last_modified": last_modified.isoformat()
    }
    if rating is not None:
        update_data["rating"] = rating
    if comment is not None:
        update_data["comment"] = comment
    result = feedback_collection.update_one(
        {"feedbackId": feedbackId},
        {"$set": update_data}
    )
    return result.modified_count > 0


def log_audit(audit_log):
    """
    Audit Logging Integration
    Sends audit log to centralized Audit and Logging Microservice via HTTP POST.
    """
    try:
        payload = {
            "service": "review_feedback",
            "action": audit_log.get("action"),
            "level": "INFO",
            "user_id": audit_log.get("userId"),
            "details": audit_log
        }
        resp = requests.post(f"{AUDIT_SERVICE_URL}/log", json=payload)
    # Audit Logging Integration
    # Sends audit log to centralized Audit and Logging Microservice via HTTP POST.
        return resp.status_code == 201
    except Exception as e:
        print(f"Failed to send audit log: {e}")
        return False

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

    # Authentication Integration
    # Extract and verify JWT token from Authorization header
    auth_header = request.headers.get("Authorization")
    user = verify_token(auth_header)
    if not user:
        return error_response("Unauthorized", 401)
    # user['id'] is now trusted and used for feedback creation

    entityId = data.get("entityId")
    rating = data.get("rating")
    comment = data.get("comment")

    # Validation
    if not all([entityId, rating]):
        return error_response("Missing required fields (entityId, rating)")

    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return error_response("Rating must be an integer between 1 and 5")

    userId = user["id"]
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

    # Authentication Integration
    # Extract and verify JWT token from Authorization header
    auth_header = request.headers.get("Authorization")
    user = verify_token(auth_header)
    if not user:
        return error_response("Unauthorized", 401)
    # user['id'] is now trusted and used for feedback update and authorization

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

    if original_feedback.get("userId") != user["id"]:
        return error_response("Unauthorized", 403)

    audit_log = {
        "auditId": str(uuid.uuid4()),
        "feedbackId": feedbackId,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "userId": user["id"],
        "action": "UPDATE",
        "before": {
            "rating": original_feedback.get("rating"),
            "comment": original_feedback.get("comment")
        },
        "after": {
            "rating": rating,
            "comment": comment
        }
    }
    log_audit(audit_log)

    update_feedback_entry(feedbackId, rating, comment, datetime.now(timezone.utc))

    return jsonify({
        "message": "Feedback updated",
        "feedbackId": feedbackId,
        "changes": audit_log["after"]
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5005"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
