from flask import Flask, jsonify, redirect, url_for, render_template, request 
from flask_cors import CORS
import os

app = Flask(__name__)

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": [o.strip() for o in allowed_origins if o.strip()],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route("/health")
def health():
    return jsonify({"message": "Review annd Feedback Microservice Online"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5005"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)