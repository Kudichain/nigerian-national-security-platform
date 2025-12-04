# WebRTC Signaling Server

## Overview
WebSocket signaling server for establishing WebRTC peer-to-peer connections between drones, cameras, and monitoring clients.

## Features
- ✅ WebSocket-based signaling for WebRTC
- ✅ Offer/Answer/ICE candidate exchange
- ✅ Client registration and discovery
- ✅ Session management
- ✅ Heartbeat/keep-alive support
- ✅ Graceful shutdown handling

## Installation

```bash
cd services/signaling
npm install
```

## Usage

### Start the server
```bash
npm start
```

### Development mode (auto-restart)
```bash
npm run dev
```

The server will start on port **8081** by default.

## Client Connection

### JavaScript/TypeScript Example

```typescript
const ws = new WebSocket('ws://localhost:8081');

// Register client
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'register',
    id: 'drone-alpha-001'
  }));
};

// Handle messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'registered':
      console.log('Registered with ID:', data.id);
      break;
      
    case 'offer':
      // Handle incoming WebRTC offer
      handleOffer(data.sdp, data.from);
      break;
      
    case 'answer':
      // Handle WebRTC answer
      handleAnswer(data.sdp, data.from);
      break;
      
    case 'ice':
      // Handle ICE candidate
      handleICE(data.candidate, data.from);
      break;
  }
};

// Send WebRTC offer
function sendOffer(targetId, sdpOffer) {
  ws.send(JSON.stringify({
    type: 'offer',
    target: targetId,
    sdp: sdpOffer
  }));
}

// Send WebRTC answer
function sendAnswer(targetId, sdpAnswer) {
  ws.send(JSON.stringify({
    type: 'answer',
    target: targetId,
    sdp: sdpAnswer
  }));
}

// Send ICE candidate
function sendICE(targetId, candidate) {
  ws.send(JSON.stringify({
    type: 'ice',
    target: targetId,
    candidate: candidate
  }));
}
```

## Message Types

### Client → Server

#### 1. Register
```json
{
  "type": "register",
  "id": "client-unique-id"
}
```

#### 2. Send Offer
```json
{
  "type": "offer",
  "target": "target-client-id",
  "sdp": "v=0\r\no=...",
  "sessionId": "optional-session-id"
}
```

#### 3. Send Answer
```json
{
  "type": "answer",
  "target": "caller-client-id",
  "sdp": "v=0\r\na=...",
  "sessionId": "session-id"
}
```

#### 4. Send ICE Candidate
```json
{
  "type": "ice",
  "target": "peer-client-id",
  "candidate": {
    "candidate": "candidate:...",
    "sdpMLineIndex": 0,
    "sdpMid": "0"
  }
}
```

#### 5. List Clients
```json
{
  "type": "list"
}
```

#### 6. Heartbeat
```json
{
  "type": "ping"
}
```

### Server → Client

#### 1. Registration Confirmation
```json
{
  "type": "registered",
  "id": "client-unique-id",
  "timestamp": "2025-11-27T12:00:00.000Z"
}
```

#### 2. Incoming Offer
```json
{
  "type": "offer",
  "from": "sender-client-id",
  "sdp": "v=0\r\no=...",
  "sessionId": "session-abc123",
  "timestamp": "2025-11-27T12:00:00.000Z"
}
```

#### 3. Incoming Answer
```json
{
  "type": "answer",
  "from": "responder-client-id",
  "sdp": "v=0\r\na=...",
  "sessionId": "session-abc123",
  "timestamp": "2025-11-27T12:00:00.000Z"
}
```

#### 4. ICE Candidate
```json
{
  "type": "ice",
  "from": "peer-client-id",
  "candidate": {...},
  "sessionId": "session-abc123",
  "timestamp": "2025-11-27T12:00:00.000Z"
}
```

#### 5. Client List
```json
{
  "type": "clients",
  "clients": ["drone-1", "camera-2", "operator-3"],
  "count": 3
}
```

#### 6. Pong (Heartbeat Response)
```json
{
  "type": "pong",
  "timestamp": "2025-11-27T12:00:00.000Z"
}
```

#### 7. Error
```json
{
  "type": "error",
  "message": "Target client not found",
  "details": "..."
}
```

## Security Considerations

### Production Deployment Checklist
- [ ] Enable TLS/WSS (wss://) for encrypted connections
- [ ] Implement authentication (JWT tokens)
- [ ] Add rate limiting to prevent DoS
- [ ] Validate all client IDs and session IDs
- [ ] Log all signaling events for audit trail
- [ ] Use mTLS for drone/camera connections
- [ ] Implement RBAC (Role-Based Access Control)
- [ ] Add session timeouts and cleanup
- [ ] Monitor connection metrics
- [ ] Deploy behind reverse proxy (nginx/Caddy)

### Example: Adding JWT Authentication

```javascript
const jwt = require('jsonwebtoken');

wss.on('connection', (ws, req) => {
  // Extract token from query param or header
  const token = new URL(req.url, 'ws://localhost').searchParams.get('token');
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    // Allow connection for authorized user
    ws.userId = decoded.userId;
    ws.role = decoded.role;
  } catch (error) {
    ws.close(1008, 'Unauthorized');
    return;
  }
  
  // Continue with normal flow...
});
```

## Environment Variables

Create `.env` file:

```env
PORT=8081
JWT_SECRET=your-secret-key
LOG_LEVEL=info
MAX_CLIENTS=1000
HEARTBEAT_INTERVAL=30000
```

## Logging

Server logs include:
- 📱 New connections
- ✅ Client registrations
- 📤 Message forwarding
- 👋 Disconnections
- ❌ Errors
- 🧊 ICE candidate exchanges

## Monitoring

Health check endpoint (add to server.js):

```javascript
const express = require('express');
const app = express();

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    clients: clients.size,
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});

app.listen(8082);
```

## Scaling

For high-traffic production:
- Use Redis Pub/Sub for multi-server signaling
- Implement load balancing with sticky sessions
- Consider dedicated media servers (Janus, Kurento, mediasoup)
- Use TURN servers for NAT traversal

## License
MIT
