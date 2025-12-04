"""Auth risk scoring inference service."""

from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
import lightgbm as lgb
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUEST_COUNT = Counter('auth_requests_total', 'Total auth risk checks')
HIGH_RISK_COUNT = Counter('auth_high_risk_total', 'Total high-risk auth events')

MODEL_PATH = Path("models/auth/lightgbm_model.txt")
FEATURES_PATH = Path("models/auth/features.pkl")

model = lgb.Booster(model_file=str(MODEL_PATH))
feature_names = joblib.load(FEATURES_PATH)

logger.info("Auth risk scoring service initialized")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "auth"}), 200


@app.route("/score", methods=["POST"])
def score():
    """Score authentication event for risk."""
    REQUEST_COUNT.inc()
    
    try:
        payload = request.json
        
        # Extract features
        features = np.array([[payload.get(feat, 0.0) for feat in feature_names]])
        
        # Predict
        risk_score = float(model.predict(features)[0])
        
        # Determine action based on risk score
        if risk_score > 0.8:
            action = "block"
            HIGH_RISK_COUNT.inc()
        elif risk_score > 0.5:
            action = "challenge_mfa"
        else:
            action = "allow"
        
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": "auth",
            "score": risk_score,
            "confidence": abs(risk_score - 0.5) * 2,  # Distance from decision boundary
            "action": action,
            "model_version": "lightgbm_v1"
        }
        
        logger.info(f"Auth risk score: {risk_score:.4f}, action: {action}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
