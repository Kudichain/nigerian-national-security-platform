"""Phishing detection inference service."""

from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUEST_COUNT = Counter('phishing_requests_total', 'Total phishing checks')
PHISHING_DETECTED = Counter('phishing_detected_total', 'Total phishing emails detected')

MODEL_PATH = Path("models/phishing/tfidf_model.pkl")
vectorizer, model = joblib.load(MODEL_PATH)

logger.info("Phishing detection service initialized")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "phishing"}), 200


@app.route("/score", methods=["POST"])
def score():
    """Score email for phishing."""
    REQUEST_COUNT.inc()
    
    try:
        payload = request.json
        email_text = payload.get("body_text", "")
        subject = payload.get("subject", "")
        
        # Combine text
        full_text = f"{subject} {email_text}"
        
        # Vectorize
        X = vectorizer.transform([full_text])
        
        # Predict
        proba = float(model.predict_proba(X)[0, 1])
        is_phishing = proba > 0.5
        
        if is_phishing:
            PHISHING_DETECTED.inc()
        
        # Determine action based on score
        if proba > 0.9:
            action = "block"
        elif proba > 0.5:
            action = "quarantine"
        else:
            action = "allow"
        
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": "phishing",
            "score": proba,
            "label": "phishing" if is_phishing else "legitimate",
            "confidence": max(proba, 1 - proba),
            "action": action,
            "model_version": "tfidf_v1"
        }
        
        logger.info(f"Phishing score: {proba:.4f}, label: {response['label']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
