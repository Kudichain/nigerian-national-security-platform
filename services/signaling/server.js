// WebSocket Signaling Server for WebRTC
// Handles WebRTC offer/answer/ICE candidate exchange between peers
// Usage: node server.js

const http = require('http');
const WebSocket = require('ws');

const server = http.createServer();
const wss = new WebSocket.Server({ server });

const clients = new Map(); // clientId -> ws connection
const sessions = new Map(); // sessionId -> { caller, callee }

console.log('🚀 WebRTC Signaling Server starting...');

wss.on('connection', (ws, req) => {
  let clientId = null;
  const clientIp = req.socket.remoteAddress;
  
  console.log(`📱 New connection from ${clientIp}`);

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log(`📨 Received from ${clientId || 'unregistered'}:`, data.type);

      switch (data.type) {
        case 'register':
          // Client registration
          clientId = data.id;
          clients.set(clientId, ws);
          ws.send(JSON.stringify({
            type: 'registered',
            id: clientId,
            timestamp: new Date().toISOString(),
          }));
          console.log(`✅ Client registered: ${clientId} (total: ${clients.size})`);
          break;

        case 'offer':
          // Forward WebRTC offer to target peer
          if (!data.target) {
            ws.send(JSON.stringify({ type: 'error', message: 'No target specified' }));
            return;
          }
          const targetClient = clients.get(data.target);
          if (targetClient && targetClient.readyState === WebSocket.OPEN) {
            targetClient.send(JSON.stringify({
              type: 'offer',
              from: clientId,
              sdp: data.sdp,
              sessionId: data.sessionId || generateSessionId(),
              timestamp: new Date().toISOString(),
            }));
            console.log(`📤 Offer forwarded: ${clientId} -> ${data.target}`);
          } else {
            ws.send(JSON.stringify({
              type: 'error',
              message: `Target ${data.target} not found or offline`,
            }));
          }
          break;

        case 'answer':
          // Forward WebRTC answer to caller
          if (!data.target) {
            ws.send(JSON.stringify({ type: 'error', message: 'No target specified' }));
            return;
          }
          const caller = clients.get(data.target);
          if (caller && caller.readyState === WebSocket.OPEN) {
            caller.send(JSON.stringify({
              type: 'answer',
              from: clientId,
              sdp: data.sdp,
              sessionId: data.sessionId,
              timestamp: new Date().toISOString(),
            }));
            console.log(`📤 Answer forwarded: ${clientId} -> ${data.target}`);
          } else {
            ws.send(JSON.stringify({
              type: 'error',
              message: `Caller ${data.target} not found or offline`,
            }));
          }
          break;

        case 'ice':
          // Forward ICE candidate to peer
          if (!data.target) {
            ws.send(JSON.stringify({ type: 'error', message: 'No target specified' }));
            return;
          }
          const peer = clients.get(data.target);
          if (peer && peer.readyState === WebSocket.OPEN) {
            peer.send(JSON.stringify({
              type: 'ice',
              from: clientId,
              candidate: data.candidate,
              sessionId: data.sessionId,
              timestamp: new Date().toISOString(),
            }));
            console.log(`🧊 ICE candidate forwarded: ${clientId} -> ${data.target}`);
          }
          break;

        case 'list':
          // List available clients (for UI)
          const availableClients = Array.from(clients.keys()).filter(id => id !== clientId);
          ws.send(JSON.stringify({
            type: 'clients',
            clients: availableClients,
            count: availableClients.length,
          }));
          break;

        case 'ping':
          // Heartbeat / keep-alive
          ws.send(JSON.stringify({
            type: 'pong',
            timestamp: new Date().toISOString(),
          }));
          break;

        default:
          console.warn(`⚠️ Unknown message type: ${data.type}`);
          ws.send(JSON.stringify({
            type: 'error',
            message: `Unknown message type: ${data.type}`,
          }));
      }
    } catch (error) {
      console.error('❌ Error processing message:', error.message);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format',
        details: error.message,
      }));
    }
  });

  ws.on('close', () => {
    if (clientId) {
      clients.delete(clientId);
      console.log(`👋 Client disconnected: ${clientId} (remaining: ${clients.size})`);
      
      // Notify other clients
      broadcastClientList();
    }
  });

  ws.on('error', (error) => {
    console.error(`❌ WebSocket error for ${clientId || 'unregistered'}:`, error.message);
  });
});

// Helper functions
function generateSessionId() {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function broadcastClientList() {
  const clientList = Array.from(clients.keys());
  const message = JSON.stringify({
    type: 'client_list_update',
    clients: clientList,
    count: clientList.length,
    timestamp: new Date().toISOString(),
  });

  clients.forEach((ws, clientId) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(message);
    }
  });
}

// Server configuration
const PORT = process.env.PORT || 8081;
server.listen(PORT, () => {
  console.log(`✅ Signaling server running on port ${PORT}`);
  console.log(`🔗 WebSocket endpoint: ws://localhost:${PORT}`);
  console.log(`📡 Ready to handle WebRTC connections\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down signaling server...');
  wss.clients.forEach((ws) => {
    ws.close(1000, 'Server shutting down');
  });
  server.close(() => {
    console.log('✅ Server closed gracefully');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 SIGTERM received, shutting down...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});
