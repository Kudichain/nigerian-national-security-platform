"""Authentication risk scoring model training."""

import pandas as pd
from pathlib import Path
import lightgbm as lgb
import joblib
import mlflow
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthRiskTrainer:
    """Train authentication risk scoring models."""
    
    def __init__(self, experiment_name: str = "sec-ai-auth") -> None:
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
    
    def train_lightgbm(self, data_path: str) -> lgb.Booster:
        """Train LightGBM for fast auth risk scoring."""
        df = pd.read_parquet(data_path)
        
        feature_cols = [col for col in df.columns if col not in ['label', 'ts', 'user_id']]
        X = df[feature_cols].fillna(0)
        y = (df['label'] == 'fraud').astype(int)
        
        with mlflow.start_run(run_name=f"auth_lgbm_{datetime.now():%Y%m%d_%H%M%S}"):
            dtrain = lgb.Dataset(X, label=y)
            
            params = {
                'objective': 'binary',
                'metric': 'auc',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9
            }
            
            bst = lgb.train(params, dtrain, num_boost_round=200)
            
            model_path = Path("models/auth/lightgbm_model.txt")
            model_path.parent.mkdir(parents=True, exist_ok=True)
            bst.save_model(str(model_path))
            
            joblib.dump(feature_cols, model_path.parent / "features.pkl")
            mlflow.log_artifact(str(model_path))
            
            logger.info(f"Auth risk model saved to {model_path}")
        
        return bst


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()
    
    trainer = AuthRiskTrainer()
    trainer.train_lightgbm(args.data)
