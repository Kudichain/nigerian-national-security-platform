# MLOps Guide

## Model Lifecycle

### 1. Experimentation

Use Jupyter notebooks for exploration:

```powershell
jupyter notebook notebooks/
```

### 2. Training

All training scripts log to MLflow:

```powershell
# Set MLflow tracking URI
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"

# Train model
python models/nids/train.py --data data/netflow.parquet
```

### 3. Model Registry

Register model in MLflow:

```python
import mlflow

client = mlflow.tracking.MlflowClient()

# Register model
model_uri = "runs:/RUN_ID/model"
result = mlflow.register_model(model_uri, "nids-isoforest")

# Promote to production
client.transition_model_version_stage(
    name="nids-isoforest",
    version=1,
    stage="Production"
)
```

### 4. Deployment

```powershell
# Build Docker image with new model
docker build -t sec-ai/nids:v2 -f infra/docker/Dockerfile.nids .

# Push to registry
docker push sec-ai/nids:v2

# Update K8s deployment
kubectl set image deployment/nids-inference nids=sec-ai/nids:v2 -n sec-ai

# Rollout status
kubectl rollout status deployment/nids-inference -n sec-ai
```

### 5. Monitoring

Monitor model performance:

- Prediction distribution
- Latency
- Error rate
- Drift detection

```python
# Log custom metrics
import mlflow
mlflow.log_metric("prediction_mean", score.mean())
mlflow.log_metric("false_positive_rate", fpr)
```

## Drift Detection

Monitor feature and prediction drift:

```python
from scipy.stats import ks_2samp

# Compare training vs production distributions
def detect_drift(train_data, prod_data, threshold=0.05):
    """Detect drift using Kolmogorov-Smirnov test."""
    statistic, p_value = ks_2samp(train_data, prod_data)
    
    if p_value < threshold:
        return True, p_value
    return False, p_value
```

## A/B Testing

Deploy two model versions:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nids-service
spec:
  selector:
    app: nids
  ports:
  - port: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nids-v1
spec:
  replicas: 8
  selector:
    matchLabels:
      app: nids
      version: v1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nids-v2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nids
      version: v2
```

## Retraining Pipeline

Automated retraining with Kubernetes CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nids-retrain
  namespace: sec-ai
spec:
  schedule: "0 2 * * 0"  # Weekly on Sunday at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: train
            image: sec-ai/nids-train:latest
            command:
            - python
            - models/nids/train.py
            - --data
            - s3://sec-ai-raw/netflow/2025-11-*.parquet
            env:
            - name: MLFLOW_TRACKING_URI
              value: http://mlflow:5000
          restartPolicy: OnFailure
```

## Model Versioning

Best practices:

1. **Semantic versioning**: `major.minor.patch`
2. **Tag with metadata**: training date, dataset version
3. **Immutable artifacts**: never overwrite existing models
4. **Signature logging**: log input/output schemas

```python
import mlflow
from mlflow.models.signature import infer_signature

# Infer signature
signature = infer_signature(X_train, model.predict(X_train))

# Log with signature
mlflow.sklearn.log_model(
    model,
    "model",
    signature=signature,
    registered_model_name="nids-isoforest"
)
```

## Performance Tracking

Track key metrics:

- **Model metrics**: AUC, precision@k, recall
- **Business metrics**: alerts per day, false positive rate
- **Operational metrics**: latency, throughput

```python
# Log all metrics
mlflow.log_metrics({
    "auc": 0.95,
    "precision_at_100": 0.89,
    "avg_latency_ms": 45,
    "throughput_qps": 1200
})
```
