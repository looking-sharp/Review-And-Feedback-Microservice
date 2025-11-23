from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone
import os
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

# MongoDB Connection (Olivia)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["review_feedback_db"]
feedback_collection = db["feedbacks"]

def error_response(message, code=400):
    return jsonify({"error": message}), code

#  Database Helper Functions
def get_feedback(feedbackId):
    """
    Olivia: Replace MOCK_DB lookup with actual DB query. 
    """
    feedback = feedback_collection.find_one({"feedbackId": feedbackId})
    if feedback:
        feedback.pop("_id", None)
    return feedback


def save_feedback(userId, entityId, rating, comment):
    """
    Olivia: Replace MOCK_DB insertion with actual DB insert logic. 
    """
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
    """
    Olivia: Replace MOCK_DB update with actual DB UPDATE logic.
    Update feedback in MongoDB (provided fields only, refresh timestamp).
    """
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

    update_feedback_entry(feedbackId, rating, comment, datetime.now(timezone.utc))

    return jsonify({
        "message": "Feedback updated",
        "feedbackId": feedbackId,
        "changes": {"rating": rating, "comment": comment}
    }), 200

"""

Get feedback (Thomas)

"""

def get_parameters(args) -> dict:
    # get by ID
    _id = args.get("id")
    if _id:
        return {"id": _id}
    
    # get by recent (default get all newest -> oldest)
    amount = args.get("amount", -1)
    start_at = args.get("start", 0)
    order = args.get("order", "desc").lower()
    
    return {"amount": amount, "start_at": start_at, "order": order}

@app.route("/get-feedback", methods=["GET"])
def get_feedback_list():
    # get parameters
    params = get_parameters(request.args)
    if "id" in params:
        # get only review with that id:
        log = feedback_collection.find_one({"feedbackId": params["id"]})
        if log:
            log.pop("_id", None)
            return jsonify({"result": log}), 200
        return jsonify({"error": "feedback not found"}),400
    
    amount = int(params["amount"])
    start_at = int(params["start_at"])
    order = params["order"]
    sort_direction = -1 if order == "desc" else 1

    # grab all feedback and sort by order
    query = feedback_collection.find().sort("last_modified", sort_direction)

    if start_at > 0:
        query = query.skip(start_at)

    if amount > -1:
        query = query.limit(amount)

    results = []
    for doc in query:
        doc.pop("_id", None)
        results.append(doc)

    return jsonify({"results": results}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5005"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
