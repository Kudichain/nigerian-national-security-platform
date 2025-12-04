"""Phishing detection model training."""

import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhishingTrainer:
    """Train phishing detection models."""
    
    def __init__(self, experiment_name: str = "sec-ai-phishing") -> None:
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
    
    def train_tfidf_model(self, data_path: str) -> tuple:
        """Train TF-IDF + Logistic Regression."""
        df = pd.read_parquet(data_path)
        
        with mlflow.start_run(run_name=f"phishing_tfidf_{datetime.now():%Y%m%d_%H%M%S}"):
            vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
            X = vectorizer.fit_transform(df['body_text'].fillna(''))
            y = (df['label'] == 'phishing').astype(int)
            
            clf = LogisticRegression(max_iter=1000, random_state=42)
            clf.fit(X, y)
            
            model_path = Path("models/phishing/tfidf_model.pkl")
            model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump((vectorizer, clf), model_path)
            
            mlflow.sklearn.log_model(clf, "model")
            logger.info(f"Phishing model saved to {model_path}")
        
        return vectorizer, clf
    
    def train_feature_based_model(self, data_path: str) -> xgb.XGBClassifier:
        """Train XGBoost on extracted features."""
        df = pd.read_parquet(data_path)
        
        feature_cols = [col for col in df.columns if col not in ['label', 'ts', 'msg_id']]
        X = df[feature_cols].fillna(0)
        y = (df['label'] == 'phishing').astype(int)
        
        with mlflow.start_run(run_name=f"phishing_xgb_{datetime.now():%Y%m%d_%H%M%S}"):
            clf = xgb.XGBClassifier(n_estimators=200, random_state=42)
            clf.fit(X, y)
            
            model_path = Path("models/phishing/xgb_model.pkl")
            joblib.dump(clf, model_path)
            mlflow.xgboost.log_model(clf, "model")
            
        return clf


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", default="tfidf", choices=["tfidf", "xgboost"])
    args = parser.parse_args()
    
    trainer = PhishingTrainer()
    if args.model == "tfidf":
        trainer.train_tfidf_model(args.data)
    else:
        trainer.train_feature_based_model(args.data)
