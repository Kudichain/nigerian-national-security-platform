# API Reference

## Common Response Format

All inference services return a standardized response:

```json
{
  "timestamp": "2025-11-27T10:30:00Z",
  "domain": "nids|logs|phishing|auth|malware",
  "score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "label": "string",
  "action": "allow|alert|block|quarantine|challenge_mfa",
  "explanation": [
    {
      "feature": "feature_name",
      "contribution": 0.45
    }
  ],
  "model_version": "string",
  "metadata": {}
}
```

## NIDS API

### POST /score

Score network flow for anomalies.

**Request**:
```json
{
  "bytes": 1024,
  "packets": 10,
  "duration_ms": 500,
  "protocol": "TCP",
  "dst_port": 443,
  "src_ip": "192.168.1.100",
  "dst_ip": "8.8.8.8"
}
```

**Response**:
```json
{
  "timestamp": "2025-11-27T10:30:00Z",
  "domain": "nids",
  "score": -0.23,
  "anomaly": true,
  "confidence": 0.85,
  "action": "alert",
  "explanation": [
    {"feature": "bytes_per_second", "contribution": 0.45},
    {"feature": "dst_port", "contribution": 0.23}
  ]
}
```

## Phishing API

### POST /score

Classify email as phishing or legitimate.

**Request**:
```json
{
  "from_addr": "sender@example.com",
  "subject": "Account verification required",
  "body_text": "Click here to verify your account...",
  "urls": ["http://suspicious-site.xyz"],
  "spf_result": "fail"
}
```

**Response**:
```json
{
  "timestamp": "2025-11-27T10:30:00Z",
  "domain": "phishing",
  "score": 0.92,
  "label": "phishing",
  "confidence": 0.92,
  "action": "quarantine",
  "model_version": "tfidf_v1"
}
```

## Auth Risk API

### POST /score

Score authentication event for fraud risk.

**Request**:
```json
{
  "user_id": "user123",
  "ip": "198.51.100.42",
  "geo": "RU",
  "device_id": "new_device",
  "mfa_used": false,
  "failures_last_1h": 3
}
```

**Response**:
```json
{
  "timestamp": "2025-11-27T10:30:00Z",
  "domain": "auth",
  "score": 0.85,
  "confidence": 0.70,
  "action": "challenge_mfa",
  "model_version": "lightgbm_v1"
}
```

## Health Check

All services expose `/health` endpoint:

### GET /health

**Response**:
```json
{
  "status": "healthy",
  "service": "nids"
}
```

## Metrics

All services expose Prometheus metrics at `/metrics`:

### GET /metrics

Returns Prometheus-formatted metrics:
```
# HELP nids_requests_total Total NIDS inference requests
# TYPE nids_requests_total counter
nids_requests_total 12345

# HELP nids_anomalies_total Total anomalies detected
# TYPE nids_anomalies_total counter
nids_anomalies_total 123

# HELP nids_request_latency_seconds NIDS inference latency
# TYPE nids_request_latency_seconds histogram
nids_request_latency_seconds_bucket{le="0.01"} 9500
nids_request_latency_seconds_bucket{le="0.05"} 11800
```

## Error Responses

All errors return standard format:

```json
{
  "error": "Error message",
  "timestamp": "2025-11-27T10:30:00Z",
  "status": 500
}
```

## Rate Limiting

- Default: 60 requests/minute per API key
- Returns `429 Too Many Requests` when exceeded
- Header: `X-RateLimit-Remaining: 45`

## Authentication

Include API key in header:

```
X-API-Key: your_api_key_here
```
