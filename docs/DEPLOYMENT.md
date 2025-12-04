# Deployment Guide

## Infrastructure Setup

### 1. Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Helm 3.x
- Docker registry access
- S3 or compatible object storage
- Domain for ingress (optional)

### 2. Deploy Core Infrastructure

```powershell
# Create namespace
kubectl create namespace sec-ai

# Deploy common resources
kubectl apply -f infra/k8s/common.yaml

# Deploy Kafka
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka -n sec-ai

# Deploy Redis
helm install redis bitnami/redis -n sec-ai

# Deploy PostgreSQL
helm install postgres bitnami/postgresql -n sec-ai `
  --set auth.database=secai_metadata `
  --set auth.username=secai `
  --set auth.password=changeme

# Deploy MLflow
kubectl apply -f infra/k8s/mlflow-deployment.yaml
```

### 3. Configure Secrets

```powershell
# AWS credentials
kubectl create secret generic aws-credentials -n sec-ai `
  --from-literal=access-key-id=YOUR_KEY `
  --from-literal=secret-access-key=YOUR_SECRET

# Database passwords
kubectl create secret generic db-passwords -n sec-ai `
  --from-literal=postgres-password=STRONG_PASSWORD `
  --from-literal=redis-password=STRONG_PASSWORD
```

### 4. Deploy Inference Services

```powershell
# NIDS
kubectl apply -f infra/k8s/nids-deployment.yaml

# Phishing
kubectl apply -f infra/k8s/phishing-deployment.yaml

# Auth Risk
kubectl apply -f infra/k8s/auth-deployment.yaml

# Verify deployments
kubectl get pods -n sec-ai
kubectl get svc -n sec-ai
```

### 5. Deploy Monitoring

```powershell
# Prometheus
helm install prometheus prometheus-community/prometheus -n sec-ai

# Grafana
helm install grafana grafana/grafana -n sec-ai `
  --set adminPassword=admin

# Get Grafana password
kubectl get secret grafana -n sec-ai -o jsonpath="{.data.admin-password}" | base64 -d
```

### 6. Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sec-ai-ingress
  namespace: sec-ai
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.sec-ai.example.com
    secretName: sec-ai-tls
  rules:
  - host: api.sec-ai.example.com
    http:
      paths:
      - path: /nids
        pathType: Prefix
        backend:
          service:
            name: nids-service
            port:
              number: 80
```

## Scaling

### Horizontal Pod Autoscaling

```powershell
# Enable metrics server (if not installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# HPA is already configured in deployment files
kubectl get hpa -n sec-ai
```

### Manual Scaling

```powershell
kubectl scale deployment nids-inference --replicas=5 -n sec-ai
```

## Monitoring

Access dashboards:

```powershell
# Grafana
kubectl port-forward svc/grafana 3000:80 -n sec-ai
# Navigate to http://localhost:3000

# Prometheus
kubectl port-forward svc/prometheus-server 9090:80 -n sec-ai
# Navigate to http://localhost:9090

# MLflow
kubectl port-forward svc/mlflow 5000:5000 -n sec-ai
# Navigate to http://localhost:5000
```

## Troubleshooting

### Check logs

```powershell
# Service logs
kubectl logs -f deployment/nids-inference -n sec-ai

# Previous container logs (if crashed)
kubectl logs deployment/nids-inference -n sec-ai --previous

# All pods in namespace
kubectl logs -l app=nids -n sec-ai --tail=100
```

### Common Issues

1. **Pod not starting**: Check events
   ```powershell
   kubectl describe pod POD_NAME -n sec-ai
   ```

2. **Model not loading**: Verify PVC and model files
   ```powershell
   kubectl exec -it POD_NAME -n sec-ai -- ls /models
   ```

3. **High latency**: Check HPA and resource limits
   ```powershell
   kubectl top pods -n sec-ai
   ```

## Backup and Restore

### Backup models

```powershell
# Sync from PVC to S3
kubectl exec -it POD_NAME -n sec-ai -- aws s3 sync /models s3://sec-ai-models/backup/
```

### Restore models

```powershell
# Sync from S3 to PVC
kubectl exec -it POD_NAME -n sec-ai -- aws s3 sync s3://sec-ai-models/backup/ /models
```
