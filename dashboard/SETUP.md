# Security AI Platform Dashboard - Setup Guide

## Prerequisites

- Node.js 18+ and npm
- Backend services running (see main README)

## Installation

### 1. Install Dependencies

```powershell
cd dashboard
npm install
```

This installs:
- React 18.2 + TypeScript
- Material-UI (MUI) components + icons + charts
- Vite (fast dev server + bundler)
- Zustand (state management)
- React Query (data fetching)
- Socket.IO client (real-time alerts)
- Recharts (visualizations)
- Axios (HTTP client)

### 2. Configure Environment

Create `.env` file:

```env
VITE_API_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080
```

For production, point to your deployed backend.

### 3. Start Development Server

```powershell
npm run dev
```

Dashboard available at: **http://localhost:3001**

## Project Structure

```
dashboard/
├── src/
│   ├── main.tsx                 # App entry point + MUI theme
│   ├── App.tsx                  # React Router setup
│   ├── components/
│   │   └── Layout.tsx           # Sidebar navigation + app bar
│   ├── pages/
│   │   ├── Login.tsx            # Authentication page
│   │   ├── Dashboard.tsx        # Overview with charts
│   │   ├── Alerts.tsx           # Alert management table
│   │   ├── Investigation.tsx    # Threat deep-dive
│   │   ├── Insights.tsx         # AI analytics (5 tabs)
│   │   └── Settings.tsx         # Configuration (4 tabs)
│   ├── store/
│   │   ├── authStore.ts         # User auth state (Zustand + persist)
│   │   └── alertStore.ts        # Alert state + WebSocket
│   └── api/
│       └── client.ts            # Axios instance + endpoints
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

## Features

### 1. Login Page (`Login.tsx`)

**Demo Mode**: Any username/password works.

For production JWT:
```typescript
// In authStore.ts, replace mock login with:
const { data } = await api.post('/auth/login', { username, password })
set({ user: data.user, token: data.token, isAuthenticated: true })
```

### 2. Dashboard (`Dashboard.tsx`)

**Components**:
- 5 summary cards (Total, Critical, High, Medium, Low alerts)
- Bar chart: Alerts by domain (NIDS, Logs, Phishing, Auth, Malware)
- Pie chart: Severity distribution
- Line chart: 24-hour trend
- Recent alerts table (last 10)

**Data Source**: `useAlertStore()` from Zustand

### 3. Alerts Page (`Alerts.tsx`)

**Features**:
- Real-time WebSocket updates
- Filterable DataGrid (domain, severity, status)
- Inline status editing
- Alert detail dialog
- "Investigate" button → Investigation page

**State**: WebSocket connected on mount via `useAlertStore()`

### 4. Investigation Page (`Investigation.tsx`)

**Analysis**:
- Alert metadata (domain, severity, score, confidence)
- SHAP feature importance bar chart
- Recommended mitigation actions
- Affected assets

**Route**: `/investigation/:alertId`

### 5. Insights Page (`Insights.tsx`)

**5 Tabs**:
1. **Trends**: 30-day volume + avg score line charts, false positive bar chart
2. **Feature Importance**: Global SHAP values by feature
3. **Model Performance**: Radar chart (Precision, Recall, F1, Accuracy, AUC)
4. **Entity Risk**: Top risky IPs/users with scores
5. **Attack Patterns**: Detected patterns with severity

**Domain Selector**: Switch between NIDS/Logs/Phishing/Auth/Malware

### 6. Settings Page (`Settings.tsx`)

**4 Tabs**:
1. **Thresholds**: Adjust confidence sliders per domain
2. **Trusted Entities**: Whitelist IPs/domains/emails (CRUD table)
3. **Model Management**: Select model versions, deploy updates
4. **Training**: Upload datasets, trigger retraining jobs

## State Management

### Auth Store (`authStore.ts`)

```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username, password) => Promise<void>
  logout: () => void
}
```

**Persistence**: Zustand `persist` middleware → localStorage

### Alert Store (`alertStore.ts`)

```typescript
interface AlertState {
  alerts: Alert[]
  socket: Socket | null
  connected: boolean
  addAlert: (alert) => void
  updateAlert: (id, updates) => void
  connectWebSocket: () => void
  disconnectWebSocket: () => void
}
```

**WebSocket**: Auto-connects on app load, listens for `alert` events

## API Integration

**Base URL**: `/api` (proxied to backend in dev via Vite)

**Endpoints** (defined in `api/client.ts`):

```typescript
// Alerts
GET    /api/alerts?domain=&severity=&status=
GET    /api/alerts/:id
PATCH  /api/alerts/:id

// Inference
POST   /api/nids/score
POST   /api/phishing/score
POST   /api/auth/score

// Health
GET    /api/nids/health
GET    /api/phishing/health
GET    /api/auth/health

// Insights
GET    /api/insights/:domain/stats?timeRange=
GET    /api/insights/:domain/trends

// Models
GET    /api/models
POST   /api/models/:domain/train
POST   /api/models/:domain/deploy
```

**Auth Interceptor**:
```typescript
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
```

## Styling

**Theme** (`main.tsx`):
- Dark mode by default
- Primary: `#2196f3` (blue)
- Secondary: `#f50057` (pink)
- Background: `#0a1929` (dark navy)

**Customization**:
```typescript
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#your-color' },
    // ...
  }
})
```

## Charts

**Recharts** used for all visualizations:
- `LineChart`: Trends over time
- `BarChart`: Domain counts, feature importance
- `PieChart`: Severity distribution
- `RadarChart`: Model performance metrics

**Example**:
```typescript
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={domainData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="name" />
    <YAxis />
    <Tooltip />
    <Bar dataKey="value" fill="#2196f3" />
  </BarChart>
</ResponsiveContainer>
```

## Build for Production

```powershell
npm run build
```

Output: `dist/` folder

**Preview**:
```powershell
npm run preview
```

## Deployment

### Option 1: Nginx

**Dockerfile**:
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

**nginx.conf**:
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

### Option 2: Static Hosting

Deploy `dist/` to:
- AWS S3 + CloudFront
- Netlify
- Vercel
- GitHub Pages

Configure API base URL via environment variable.

### Option 3: Kubernetes

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboard
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: dashboard
        image: security-ai-dashboard:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: dashboard
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
```

## Troubleshooting

### WebSocket Not Connecting

**Issue**: `connected: false` in app bar

**Solutions**:
1. Check backend is running and exposes WebSocket endpoint
2. Verify `VITE_WS_URL` in `.env`
3. Check browser console for connection errors
4. Ensure CORS allows WebSocket origin

### API 401 Errors

**Issue**: All requests return 401 Unauthorized

**Solutions**:
1. Check JWT token in localStorage (DevTools → Application → Local Storage)
2. Verify backend accepts token format
3. Re-login to refresh token

### Charts Not Rendering

**Issue**: Blank space where chart should be

**Solutions**:
1. Check browser console for errors
2. Verify data shape matches chart requirements
3. Ensure `ResponsiveContainer` parent has height

### Slow Performance

**Solutions**:
1. Reduce alert history (limit to last 1000 in `alertStore`)
2. Enable React.memo for expensive components
3. Use virtualization for long lists (react-window)
4. Lazy load pages with React.lazy

## Development Tips

### Hot Reload

Vite provides instant HMR. Edit any `.tsx` file and see changes immediately.

### Type Checking

```powershell
npm run lint  # ESLint
tsc --noEmit  # TypeScript compiler check
```

### Debug State

Use React DevTools extension:
- Install from Chrome Web Store
- Inspect component tree
- View Zustand state in Components panel

### Mock Data

For frontend-only development, replace API calls with mock data:

```typescript
// In api/client.ts
export const alertsApi = {
  getAlerts: async () => ({
    data: [
      { id: '1', title: 'Port scan detected', severity: 'high', ... },
      // ... more mock alerts
    ]
  })
}
```

## Performance Optimization

**Code Splitting**:
```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Alerts = lazy(() => import('./pages/Alerts'))

<Suspense fallback={<CircularProgress />}>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/alerts" element={<Alerts />} />
  </Routes>
</Suspense>
```

**Memoization**:
```typescript
const MemoizedChart = React.memo(({ data }) => (
  <BarChart data={data}>...</BarChart>
))
```

**Bundle Analysis**:
```powershell
npm run build -- --mode analyze
```

## Security

**CSP Headers** (add to nginx.conf):
```nginx
add_header Content-Security-Policy "default-src 'self'; connect-src 'self' ws://localhost:8080";
```

**XSS Protection**: React escapes by default, but validate all user input

**CSRF**: For state-changing requests, include CSRF token from backend

## Next Features

- [ ] Dark/light theme toggle
- [ ] Export insights as PDF
- [ ] Advanced graph visualizations (D3.js for network topology)
- [ ] Alert correlation timeline
- [ ] User management UI (create/edit users)
- [ ] Multi-language support (i18n)

## Resources

- [MUI Documentation](https://mui.com/)
- [Recharts Examples](https://recharts.org/en-US/examples)
- [Zustand Guide](https://github.com/pmndrs/zustand)
- [Vite Features](https://vitejs.dev/guide/features.html)

---

**Questions?** Check the main `README.md` or open an issue.
