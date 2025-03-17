import os
import json
from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get Firebase credentials from an environment variable
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

if not FIREBASE_CREDENTIALS:
    raise ValueError("Firebase credentials not set. Set FIREBASE_CREDENTIALS environment variable.")

# Parse JSON string from environment variable
try:
    cred_dict = json.loads(FIREBASE_CREDENTIALS)  # Convert JSON string to dictionary
    cred = credentials.Certificate(cred_dict)  # Use dictionary instead of file path
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    raise ValueError(f"Error initializing Firebase: {str(e)}")

def get_pothole_data():
    """Fetch pothole data from Firebase."""
    try:
        potholes_ref = db.collection("potholes_database").stream()
        data = [
            {
                "latitude": float(doc.to_dict().get("latitude", 0)),
                "longitude": float(doc.to_dict().get("longitude", 0)),
                "size": str(doc.to_dict().get("size", "")).strip().lower()
            }
            for doc in potholes_ref if doc.to_dict().get("latitude") and doc.to_dict().get("longitude")
        ]
        return data
    except Exception as e:
        print(f"Firebase Error: {str(e)}")
        return []

@app.route('/api/potholes', methods=['GET'])
def potholes():
    """API endpoint to fetch pothole data."""
    try:
        data = get_pothole_data()
        if not data:
            return jsonify({
                "success": True,
                "message": "No pothole data found",
                "data": []
            })
        return jsonify({
            "success": True,
            "count": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Server error",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
