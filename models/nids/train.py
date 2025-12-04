"""Network intrusion detection model training."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NIDSTrainer:
    """Train network intrusion detection models."""
    
    def __init__(self, experiment_name: str = "sec-ai-nids") -> None:
        """Initialize NIDS trainer."""
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
    
    def train_isolation_forest(
        self,
        data_path: str,
        contamination: float = 0.005,
        n_estimators: int = 100
    ) -> IsolationForest:
        """
        Train Isolation Forest for anomaly detection.
        
        Args:
            data_path: Path to training data (parquet)
            contamination: Expected proportion of outliers
            n_estimators: Number of trees
            
        Returns:
            Trained Isolation Forest model
        """
        logger.info(f"Loading data from {data_path}")
        df = pd.read_parquet(data_path)
        
        # Feature selection
        feature_cols = [
            'bytes', 'packets', 'duration_ms', 'bytes_per_packet',
            'packets_per_second', 'bytes_per_second', 'protocol_tcp',
            'protocol_udp', 'protocol_icmp', 'dst_port', 'is_well_known_port'
        ]
        
        X = df[feature_cols].fillna(0)
        
        # Train model
        with mlflow.start_run(run_name=f"isolation_forest_{datetime.now():%Y%m%d_%H%M%S}"):
            # Log parameters
            mlflow.log_params({
                "model_type": "IsolationForest",
                "contamination": contamination,
                "n_estimators": n_estimators,
                "n_samples": len(X),
                "n_features": len(feature_cols),
            })
            
            # Normalize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train
            logger.info("Training Isolation Forest...")
            clf = IsolationForest(
                contamination=contamination,
                n_estimators=n_estimators,
                random_state=42,
                n_jobs=-1,
                verbose=1
            )
            clf.fit(X_scaled)
            
            # Evaluate on training data (for monitoring)
            scores = clf.decision_function(X_scaled)
            predictions = clf.predict(X_scaled)
            anomaly_ratio = (predictions == -1).sum() / len(predictions)
            
            # Log metrics
            mlflow.log_metrics({
                "anomaly_ratio": anomaly_ratio,
                "mean_score": scores.mean(),
                "std_score": scores.std(),
            })
            
            # Save artifacts
            model_path = Path("models/nids/isoforest_model.pkl")
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            joblib.dump(clf, model_path)
            joblib.dump(scaler, model_path.parent / "scaler.pkl")
            joblib.dump(feature_cols, model_path.parent / "features.pkl")
            
            # Log model
            mlflow.sklearn.log_model(clf, "model")
            mlflow.log_artifact(str(model_path))
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Anomaly ratio: {anomaly_ratio:.4f}")
        
        return clf
    
    def train_xgboost_supervised(
        self,
        data_path: str,
        label_col: str = "label"
    ) -> xgb.XGBClassifier:
        """
        Train XGBoost classifier (for labeled data).
        
        Args:
            data_path: Path to labeled training data
            label_col: Name of label column
            
        Returns:
            Trained XGBoost model
        """
        logger.info(f"Loading labeled data from {data_path}")
        df = pd.read_parquet(data_path)
        
        # Feature selection
        feature_cols = [col for col in df.columns if col not in [label_col, 'ts', 'src_ip', 'dst_ip']]
        
        X = df[feature_cols].fillna(0)
        y = (df[label_col] == 'malicious').astype(int)
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        with mlflow.start_run(run_name=f"xgboost_{datetime.now():%Y%m%d_%H%M%S}"):
            mlflow.log_params({
                "model_type": "XGBoost",
                "n_samples_train": len(X_train),
                "n_samples_val": len(X_val),
                "n_features": len(feature_cols),
            })
            
            # Train
            logger.info("Training XGBoost...")
            clf = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                eval_metric='logloss'
            )
            
            clf.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=10
            )
            
            # Evaluate
            from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
            
            y_pred = clf.predict(X_val)
            y_proba = clf.predict_proba(X_val)[:, 1]
            
            auc_score = roc_auc_score(y_val, y_proba)
            
            logger.info(f"Validation AUC: {auc_score:.4f}")
            logger.info("\n" + classification_report(y_val, y_pred, 
                                                     target_names=['benign', 'malicious']))
            
            # Log metrics
            mlflow.log_metrics({
                "val_auc": auc_score,
                "val_accuracy": (y_pred == y_val).mean(),
            })
            
            # Save model
            model_path = Path("models/nids/xgboost_model.pkl")
            joblib.dump(clf, model_path)
            joblib.dump(feature_cols, model_path.parent / "xgb_features.pkl")
            
            mlflow.xgboost.log_model(clf, "model")
            
            logger.info(f"Model saved to {model_path}")
        
        return clf


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train NIDS models")
    parser.add_argument("--data", type=str, required=True, help="Path to training data")
    parser.add_argument("--model", type=str, default="isoforest", 
                       choices=["isoforest", "xgboost"], help="Model type")
    parser.add_argument("--contamination", type=float, default=0.005, 
                       help="Contamination for Isolation Forest")
    
    args = parser.parse_args()
    
    trainer = NIDSTrainer()
    
    if args.model == "isoforest":
        trainer.train_isolation_forest(args.data, contamination=args.contamination)
    elif args.model == "xgboost":
        trainer.train_xgboost_supervised(args.data)
