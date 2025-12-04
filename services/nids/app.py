"""NIDS inference service with SHAP explainability."""

from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
import joblib
import numpy as np
import shap
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('nids_requests_total', 'Total NIDS inference requests')
REQUEST_LATENCY = Histogram('nids_request_latency_seconds', 'NIDS inference latency')
ANOMALY_COUNT = Counter('nids_anomalies_total', 'Total anomalies detected')

# Load model
MODEL_PATH = Path("models/nids/isoforest_model.pkl")
SCALER_PATH = Path("models/nids/scaler.pkl")
FEATURES_PATH = Path("models/nids/features.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
feature_names = joblib.load(FEATURES_PATH)

# Initialize SHAP explainer
explainer = shap.TreeExplainer(model)

logger.info("NIDS inference service initialized")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "nids"}), 200


@app.route("/score", methods=["POST"])
@REQUEST_LATENCY.time()
def score():
    """Score network flow for anomalies."""
    REQUEST_COUNT.inc()
    
    try:
        payload = request.json
        
        # Extract features in correct order
        features = np.array([[payload.get(feat, 0.0) for feat in feature_names]])
        
        # Scale
        features_scaled = scaler.transform(features)
        
        # Predict
        score = float(model.decision_function(features_scaled)[0])
        prediction = int(model.predict(features_scaled)[0])
        is_anomaly = prediction == -1
        
        if is_anomaly:
            ANOMALY_COUNT.inc()
        
        # SHAP explanation
        shap_values = explainer.shap_values(features_scaled)
        top_features = sorted(
            zip(feature_names, shap_values[0]),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": "nids",
            "score": score,
            "anomaly": is_anomaly,
            "confidence": abs(score),  # Higher absolute score = higher confidence
            "action": "alert" if is_anomaly else "allow",
            "explanation": [
                {"feature": feat, "contribution": float(val)}
                for feat, val in top_features
            ],
            "model_version": "isoforest_v1"
        }
        
        logger.info(f"NIDS score: {score:.4f}, anomaly: {is_anomaly}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
