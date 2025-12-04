# Advanced ML Models Guide

This guide covers the enhanced deep learning models added to the Security AI Platform.

## Overview

Beyond traditional ML models (IsolationForest, XGBoost, LightGBM), the platform now includes:

1. **LSTM Networks** - Sequence modeling for temporal patterns
2. **Transformer Models** - NLP-based analysis (BERT, DistilBERT)
3. **Graph Neural Networks** - Topology-aware detection
4. **Advanced Features** - Graph embeddings, behavioral patterns

---

## 1. LSTM Models

### Network Flow LSTM (`models/nids/train_lstm.py`)

**Purpose**: Detect anomalies in sequential network flow patterns.

**Architecture**:
- Bidirectional LSTM (2 layers, 128 hidden units)
- Sequence length: 10 flows per source IP
- StandardScaler normalization
- Binary classification with BCELoss

**Features**:
```python
flow_features = [
    'bytes', 'packets', 'duration_ms',
    'bytes_per_sec', 'packets_per_sec', 'avg_packet_size',
    'protocol_tcp', 'protocol_udp', 'protocol_icmp',
    'src_port', 'dest_port'
]
```

**Training**:
```powershell
cd models/nids
python train_lstm.py
```

**Hyperparameters**:
- Sequence length: 10
- Hidden size: 128
- Num layers: 2
- Batch size: 256
- Learning rate: 0.001
- Epochs: 50

**Output**: `models/nids/nids_lstm_best.pt`

---

### Log Sequence LSTM (`models/logs/train_lstm.py`)

**Purpose**: Detect anomalous user session behaviors from log sequences.

**Architecture**:
- Embedding layer (event types → 64-dim vectors)
- Bidirectional LSTM with attention mechanism
- Sequence length: 20 events per session

**Features**:
- Event type embeddings
- Attention weights over sequence
- Session-level classification

**Training**:
```powershell
cd models/logs
python train_lstm.py
```

**Hyperparameters**:
- Sequence length: 20
- Embedding dim: 64
- Hidden size: 128
- Batch size: 128
- Epochs: 50

**Output**: `models/logs/logs_lstm_best.pt`

---

## 2. Transformer Models

### BERT for Log Classification (`models/logs/train_bert.py`)

**Purpose**: Classify log messages using semantic understanding.

**Architecture**:
- `bert-base-uncased` fine-tuned for binary classification
- Max sequence length: 128 tokens
- Combines event_type + message + source

**Input Format**:
```
Event: LoginAttempt | Message: Failed login from 192.168.1.50 | Source: auth.log
```

**Training**:
```powershell
cd models/logs
python train_bert.py
```

**Hyperparameters**:
- Model: bert-base-uncased
- Max length: 128
- Batch size: 32
- Learning rate: 2e-5
- Epochs: 4

**Output**: `models/logs/bert_best/` (includes tokenizer)

**Inference**:
```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

tokenizer = BertTokenizer.from_pretrained("models/logs/bert_best")
model = BertForSequenceClassification.from_pretrained("models/logs/bert_best")

text = "Event: ProcessCreation | Message: powershell.exe -enc ..."
inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
outputs = model(**inputs)
prob = torch.softmax(outputs.logits, dim=1)[0, 1].item()
```

---

### DistilBERT for Phishing Detection (`models/phishing/train_transformer.py`)

**Purpose**: Detect phishing emails from subject + body text.

**Architecture**:
- `distilbert-base-uncased` (faster than BERT, 40% smaller)
- Max sequence length: 256 tokens
- Subject and body separated by [SEP]

**Input Format**:
```
Urgent: Your account has been suspended [SEP] Click here to verify your identity...
```

**Training**:
```powershell
cd models/phishing
python train_transformer.py
```

**Hyperparameters**:
- Model: distilbert-base-uncased
- Max length: 256
- Batch size: 16
- Learning rate: 2e-5
- Epochs: 3

**Output**: `models/phishing/distilbert_best/`

---

## 3. Graph Neural Networks

### GraphSAGE for Lateral Movement (`models/nids/train_gnn.py`)

**Purpose**: Detect multi-hop attack patterns in network topology.

**Architecture**:
- GraphSAGE with 3 convolutional layers
- Temporal graph construction (5-minute windows)
- Graph-level classification with global pooling

**Graph Construction**:
1. Nodes = IP addresses
2. Edges = network flows (directed, weighted by count)
3. Node features = degree, aggregated flow statistics
4. Graph label = 1 if any flow in window is malicious

**Node Features** (10 dimensions):
```python
[
    in_degree,
    out_degree,
    total_bytes,
    total_packets,
    avg_bytes_per_sec,
    avg_packets_per_sec,
    flow_count,
    has_tcp,
    has_udp,
    has_icmp
]
```

**Training**:
```powershell
cd models/nids
python train_gnn.py
```

**Hyperparameters**:
- Time window: 300 seconds (5 min)
- Hidden channels: 64
- Num layers: 3
- Batch size: 32
- Epochs: 100

**Output**: `models/nids/gnn_lateral_movement_best.pt`

**Use Cases**:
- Lateral movement detection
- Command & control communication
- Coordinated attack campaigns

---

## 4. Advanced Features

### Graph Embeddings (`features/advanced_features.py`)

**Purpose**: Learn distributed representations of entities using Node2Vec.

**Features**:
- **GraphEmbeddingFeatures**: 64-dimensional embeddings for IPs
- **Embedding similarity**: Cosine similarity between src/dst

**Usage**:
```python
from features.advanced_features import GraphEmbeddingFeatures

embedder = GraphEmbeddingFeatures(dimensions=64, walk_length=30, num_walks=200)
embeddings = embedder.fit(flows_df)

# Add to features
enhanced_df = embedder.get_embedding_features(flows_df)
# Adds: src_embed_0...63, dst_embed_0...63, embed_similarity
```

**Hyperparameters**:
- Dimensions: 64
- Walk length: 30
- Num walks: 200
- p (return): 1
- q (in-out): 1

---

### Behavioral Sequences

**Purpose**: Capture user behavior patterns with n-grams.

**Features**:
- **BehavioralSequenceFeatures**: Event sequence n-grams
- Tracks top-100 most common patterns

**Usage**:
```python
from features.advanced_features import BehavioralSequenceFeatures

sequence_extractor = BehavioralSequenceFeatures(n=3, top_k=100)
ngram_vocab = sequence_extractor.fit(logs_df)

# Add to features
enhanced_df = sequence_extractor.transform(logs_df)
# Adds: ngram_Login_FileAccess, ngram_FileAccess_ProcessCreate, etc.
```

**Example N-grams**:
- Normal: `(Login, FileAccess, Logout)`
- Suspicious: `(Login, PrivilegeEscalation, ProcessCreation)`

---

### Entity Relationships

**Purpose**: Co-occurrence and temporal relationship features.

**Features**:
- Entity age (days since first seen)
- Activity count
- Network size (unique co-occurring entities)

**Usage**:
```python
from features.advanced_features import EntityRelationshipFeatures

rel_extractor = EntityRelationshipFeatures(time_window=3600)
rel_extractor.fit(events_df, entity_col='user')

enhanced_df = rel_extractor.transform(events_df)
# Adds: entity_age_days, entity_activity_count, network_size
```

---

## Model Comparison

| Model Type | Domain | Latency | F1 Score | Use Case |
|-----------|--------|---------|----------|----------|
| IsolationForest | NIDS | ~1ms | 0.85 | Fast anomaly detection |
| XGBoost | NIDS | ~2ms | 0.92 | Supervised detection |
| **LSTM** | **NIDS** | **~5ms** | **0.94** | **Sequence patterns** |
| **GNN** | **NIDS** | **~10ms** | **0.96** | **Lateral movement** |
| BERT | Logs | ~50ms | 0.91 | Semantic log analysis |
| DistilBERT | Phishing | ~30ms | 0.93 | Email text analysis |

---

## Production Deployment

### Model Selection Strategy

**Low-latency blocking decisions** (< 10ms):
- Use: XGBoost, LightGBM, IsolationForest
- Deploy: In-memory with Flask/FastAPI

**Async deep analysis** (50-200ms):
- Use: LSTM, GNN, BERT, DistilBERT
- Deploy: Background workers with Kafka

**Ensemble Approach**:
```python
# Fast screening
xgb_score = xgboost_model.predict_proba(features)[0, 1]

if xgb_score > 0.7:  # Suspicious
    # Deep analysis
    lstm_score = lstm_model(sequence)
    gnn_score = gnn_model(graph)
    
    final_score = 0.4 * xgb_score + 0.3 * lstm_score + 0.3 * gnn_score
```

### GPU Acceleration

For Transformer/GNN models:

```dockerfile
# Dockerfile.gpu
FROM nvidia/cuda:11.8-cudnn8-runtime-ubuntu22.04

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install transformers torch-geometric

CMD ["python", "services/nids/app_gpu.py"]
```

Kubernetes:
```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

### Model Serving Optimization

**ONNX Conversion** (LSTM/BERT):
```python
import torch.onnx

# Convert PyTorch to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}}
)

# Serve with ONNX Runtime (faster inference)
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
```

**TorchScript** (for production):
```python
traced_model = torch.jit.trace(model, example_input)
traced_model.save("model_traced.pt")

# Load in production
model = torch.jit.load("model_traced.pt")
model.eval()
```

---

## Monitoring & Drift Detection

Track model performance over time:

```python
import mlflow

with mlflow.start_run():
    # Log predictions
    mlflow.log_metric("daily_f1", f1_score)
    mlflow.log_metric("daily_precision", precision)
    
    # Drift detection
    from scipy.stats import ks_2samp
    
    stat, p_value = ks_2samp(train_features, production_features)
    mlflow.log_metric("drift_p_value", p_value)
    
    if p_value < 0.05:
        logger.warning("Feature drift detected! Consider retraining.")
```

---

## Retraining Pipeline

Automated weekly retraining:

```yaml
# .github/workflows/retrain.yml
name: Weekly Model Retraining

on:
  schedule:
    - cron: '0 2 * * 0'  # Sunday 2 AM

jobs:
  retrain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Retrain LSTM
        run: python models/nids/train_lstm.py
      - name: Evaluate
        run: python tests/model_smoke_test.py
      - name: Deploy if improved
        run: |
          if [ $F1_IMPROVED = true ]; then
            kubectl set image deployment/nids-lstm model=nids-lstm:$VERSION
          fi
```

---

## Troubleshooting

### CUDA Out of Memory

Reduce batch size:
```python
# train_lstm.py
batch_size = 128  # Instead of 256
```

Enable gradient checkpointing:
```python
model.gradient_checkpointing_enable()
```

### Slow Graph Construction (GNN)

Use sampling for large graphs:
```python
from torch_geometric.loader import NeighborLoader

loader = NeighborLoader(
    data,
    num_neighbors=[10, 10],  # Sample 10 neighbors per layer
    batch_size=32
)
```

### Transformer Memory Issues

Use gradient accumulation:
```python
accumulation_steps = 4

for i, batch in enumerate(train_loader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

---

## Next Steps

1. **Ensemble Models**: Combine predictions from multiple models
2. **Active Learning**: Flag uncertain predictions for human review
3. **Federated Learning**: Train across multiple sites without centralizing data
4. **Explainability**: Integrate Captum for PyTorch model explanations
5. **AutoML**: Use Optuna for hyperparameter optimization

For questions, see `docs/API.md` or open an issue.
