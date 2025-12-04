# Security AI Platform - React Admin Dashboard

Production-grade admin dashboard for the Security AI Platform with real-time threat monitoring, investigation tools, AI insights, and model management.

## Features

### 🚨 Real-Time Alerts
- WebSocket-powered live alert feed
- Multi-domain filtering (NIDS, Logs, Phishing, Auth, Malware)
- Severity-based prioritization
- Status tracking workflow

### 🔍 Threat Investigation
- Deep-dive analysis with SHAP explanations
- Feature contribution visualization
- Recommended mitigation actions
- Affected asset tracking

### 📊 AI Insights & Analytics
- Alert trends over time
- Feature importance rankings
- Model performance metrics (Precision, Recall, F1, AUC-ROC)
- Entity risk scoring
- Attack pattern detection

### ⚙️ Settings & Management
- Configurable alert thresholds per domain
- Trusted entity whitelist
- Model version control and deployment
- Dataset upload for retraining

### 🔐 Authentication & RBAC
- JWT-based authentication
- Role-based access control (Admin, Analyst, Auditor)
- User session management

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **Vite** for blazing-fast builds
- **Zustand** for state management
- **React Query** for data fetching
- **Socket.IO** for real-time updates
- **Recharts** for visualizations
- **Axios** for API calls

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```powershell
cd dashboard
npm install
```

### Development

```powershell
npm run dev
```

Dashboard will be available at `http://localhost:3001`

### Build for Production

```powershell
npm run build
npm run preview
```

## Configuration

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080
```

### API Proxy

Development server proxies `/api/*` requests to backend (configured in `vite.config.ts`):

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
    },
  },
}
```

## Project Structure

```
dashboard/
├── src/
│   ├── api/
│   │   └── client.ts           # API client and endpoints
│   ├── components/
│   │   └── Layout.tsx          # Main layout with sidebar
│   ├── pages/
│   │   ├── Dashboard.tsx       # Overview dashboard
│   │   ├── Alerts.tsx          # Alert management
│   │   ├── Investigation.tsx   # Threat deep-dive
│   │   ├── Insights.tsx        # AI analytics
│   │   ├── Settings.tsx        # Configuration
│   │   └── Login.tsx           # Authentication
│   ├── store/
│   │   ├── authStore.ts        # Auth state
│   │   └── alertStore.ts       # Alert state + WebSocket
│   ├── App.tsx                 # Root component with routing
│   └── main.tsx                # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

## API Integration

### Backend Endpoints

The dashboard expects the following API endpoints:

```typescript
// Alerts
GET    /api/alerts?domain=&severity=&status=
GET    /api/alerts/:id
PATCH  /api/alerts/:id

// Inference Services
POST   /api/nids/score
POST   /api/phishing/score
POST   /api/auth/score
GET    /api/{service}/health
GET    /api/{service}/metrics

// Insights
GET    /api/insights/:domain/stats?timeRange=
GET    /api/insights/:domain/trends

// Models
GET    /api/models
POST   /api/models/:domain/train
POST   /api/models/:domain/deploy
```

### WebSocket Events

```javascript
socket.on('alert', (alert) => {
  // New alert received
})
```

## Authentication

Demo mode uses mock authentication. For production:

1. Implement JWT endpoint in backend:
   ```
   POST /api/auth/login  → { token, user }
   ```

2. Update `authStore.ts`:
   ```typescript
   login: async (username, password) => {
     const { data } = await api.post('/auth/login', { username, password })
     set({ user: data.user, token: data.token, isAuthenticated: true })
   }
   ```

## Deployment

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Nginx Config

```nginx
server {
  listen 80;
  root /usr/share/nginx/html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
  }
}
```

## Performance Optimization

- Code splitting via React.lazy()
- Data grid virtualization
- WebSocket connection pooling
- API response caching
- Chart data memoization

## Security

- XSS protection via React's default escaping
- CSRF tokens for state-changing requests
- JWT stored in memory (not localStorage)
- Content Security Policy headers
- Rate limiting on API calls

## Future Enhancements

- [ ] Advanced graph visualizations (network topology)
- [ ] Playbook automation triggers
- [ ] Integration with ticketing systems
- [ ] Multi-tenant support
- [ ] Dark/light theme toggle
- [ ] Export reports to PDF
- [ ] Alert correlation graphs

## License

MIT
