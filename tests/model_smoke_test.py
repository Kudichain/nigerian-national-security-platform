"""Simple smoke test for models."""

import joblib
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_nids_model():
    """Test NIDS model can load and predict."""
    model_path = Path("models/nids/isoforest_model.pkl")
    
    if not model_path.exists():
        logger.warning(f"Model not found: {model_path}")
        return
    
    model = joblib.load(model_path)
    scaler = joblib.load(model_path.parent / "scaler.pkl")
    
    # Synthetic input
    X = np.array([[1024, 10, 500, 102.4, 20.0, 2048.0, 1, 0, 0, 443, 0]])
    X_scaled = scaler.transform(X)
    
    score = model.decision_function(X_scaled)
    prediction = model.predict(X_scaled)
    
    assert score.shape == (1,), "Score shape mismatch"
    assert prediction.shape == (1,), "Prediction shape mismatch"
    
    logger.info(f"✓ NIDS model test passed. Score: {score[0]:.4f}")


def test_phishing_model():
    """Test phishing model can load and predict."""
    model_path = Path("models/phishing/tfidf_model.pkl")
    
    if not model_path.exists():
        logger.warning(f"Model not found: {model_path}")
        return
    
    vectorizer, model = joblib.load(model_path)
    
    # Synthetic input
    text = "Urgent: Verify your account now or it will be suspended!"
    X = vectorizer.transform([text])
    
    proba = model.predict_proba(X)
    
    assert proba.shape == (1, 2), "Probability shape mismatch"
    
    logger.info(f"✓ Phishing model test passed. Phishing prob: {proba[0, 1]:.4f}")


if __name__ == "__main__":
    logger.info("Running model smoke tests...")
    
    try:
        test_nids_model()
    except Exception as e:
        logger.error(f"NIDS test failed: {e}")
    
    try:
        test_phishing_model()
    except Exception as e:
        logger.error(f"Phishing test failed: {e}")
    
    logger.info("Smoke tests completed")
