import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  Tabs,
  Tab,
} from '@mui/material'
import {
  Fingerprint,
  TrafficOutlined,
  Gavel,
  Shield,
  Api,
} from '@mui/icons-material'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Identity() {
  const [tabValue, setTabValue] = useState(0)

  const services = [
    {
      name: 'NIMC Identity Matching',
      port: 8081,
      icon: <Fingerprint />,
      color: '#2196f3',
      description: 'Privacy-preserving identity verification with tokenized matching',
      status: 'operational',
    },
    {
      name: 'Decision Engine',
      port: 8082,
      icon: <Gavel />,
      color: '#ff9800',
      description: 'Policy-based decision engine with human-in-the-loop approval',
      status: 'operational',
    },
    {
      name: 'Traffic Control (ICS/SCADA)',
      port: 8083,
      icon: <TrafficOutlined />,
      color: '#f44336',
      description: 'IEC 62443-compliant traffic light control with safety interlocks',
      status: 'operational',
    },
    {
      name: 'NDPR Governance',
      port: 8084,
      icon: <Shield />,
      color: '#4caf50',
      description: 'Nigerian Data Protection Regulation compliance and consent management',
      status: 'operational',
    },
    {
      name: 'API Gateway',
      port: 8080,
      icon: <Api />,
      color: '#9c27b0',
      description: 'Secure API gateway with mTLS, JWT, and rate limiting',
      status: 'operational',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        National Identity Integration
      </Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        Privacy-first identity system with NIMC integration, drone surveillance, and ICS/SCADA traffic control
      </Alert>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {services.map((service) => (
          <Grid item xs={12} sm={6} md={4} key={service.port}>
            <Card sx={{ borderLeft: `4px solid ${service.color}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ color: service.color }}>{service.icon}</Box>
                  <Typography variant="h6">{service.name}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {service.description}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    Port: {service.port}
                  </Typography>
                  <Chip label={service.status.toUpperCase()} color="success" size="small" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Privacy Guarantees" />
          <Tab label="Architecture" />
          <Tab label="Compliance" />
          <Tab label="API Endpoints" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Privacy-by-Design Principles
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)' }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Tokenized Matching
                </Typography>
                <Typography variant="body2">
                  • Unlinkable pseudonyms (SHA-256 + salt)
                  <br />
                  • No raw PII transmitted
                  <br />
                  • One-way hashing prevents reversal
                  <br />• Purpose-limited tokens (30-day TTL)
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)' }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Data Minimization
                </Typography>
                <Typography variant="body2">
                  • Only essential attributes returned
                  <br />
                  • No name, address, or NIN exposed
                  <br />
                  • Image templates (not raw images)
                  <br />• 30-second TTL on edge devices
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)' }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Human Oversight
                </Typography>
                <Typography variant="body2">
                  • Operator approval required for actions
                  <br />
                  • 5-minute timeout on decisions
                  <br />
                  • Dual authorization for critical ops
                  <br />• Full audit trail (immutable)
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, bgcolor: 'rgba(156, 39, 176, 0.1)' }}>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  Secure Enclaves
                </Typography>
                <Typography variant="body2">
                  • Matching in isolated environments
                  <br />
                  • HSM-ready for key management
                  <br />
                  • Zero-knowledge proofs available
                  <br />• SGX/Nitro Enclave support
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            System Architecture
          </Typography>
          <Box sx={{ p: 3, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, fontFamily: 'monospace' }}>
            <Box component="pre" sx={{ margin: 0, fontSize: '12px', overflow: 'auto' }}>
{`┌─────────────────────────────────────────────────────────┐
│  Edge (Drone / Camera)                                  │
│  • Face detection (Haar/DNN)                            │
│  • Privacy filters (blur, TTL=30s)                      │
│  • Device attestation (RSA-2048)                        │
└────────────────────┬────────────────────────────────────┘
                     │ mTLS (Encrypted Templates)
                     ▼
┌─────────────────────────────────────────────────────────┐
│  API Gateway (Port 8080)                                │
│  • JWT Authentication                                   │
│  • Mutual TLS                                           │
│  • Rate Limiting (120 req/min)                          │
└─────┬──────────────┬──────────────┬────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Identity │  │ Decision │  │  Governance  │
│  (8081)  │  │  (8082)  │  │   (8084)     │
└──────────┘  └──────────┘  └──────────────┘
      │              │
      ▼              ▼
┌──────────┐  ┌──────────────┐
│   NIMC   │  │   Traffic    │
│   API    │  │   Control    │
│          │  │   (8083)     │
└──────────┘  └──────────────┘`}
            </Box>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Legal & Regulatory Compliance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  NDPR 2019 Compliant
                </Typography>
                <Typography variant="body2">
                  • Lawful basis: Public interest
                  <br />
                  • Data minimization enforced
                  <br />
                  • Storage limitation (30-90 days)
                  <br />• Subject access rights enabled
                </Typography>
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  IEC 62443 (ICS Safety)
                </Typography>
                <Typography variant="body2">
                  • Safety interlocks on traffic control
                  <br />
                  • Conflict prevention (no green-green)
                  <br />
                  • Fail-safe defaults
                  <br />• Watchdog timers (5-min max)
                </Typography>
              </Alert>
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="subtitle2" fontWeight="bold">
                  Additional Frameworks
                </Typography>
                <Typography variant="body2">
                  • Electoral Act 2022 (INEC voter privacy)
                  <br />
                  • Cybercrime Act 2015 (data protection)
                  <br />
                  • Freedom of Information Act 2011 (transparency)
                  <br />• NCC IoT Guidelines (device registration)
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            API Endpoints
          </Typography>
          <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, mb: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Identity Service (Port 8081)
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              POST /api/v1/match - Tokenized identity matching
              <br />
              GET /health - Health check
            </Typography>
          </Box>
          <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, mb: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Decision Engine (Port 8082)
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              POST /api/v1/evaluate - Policy evaluation
              <br />
              POST /api/v1/cases - Create approval case
              <br />
              GET /health - Health check
            </Typography>
          </Box>
          <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1, mb: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Traffic Control (Port 8083)
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              POST /api/v1/control - Issue control command (requires approval)
              <br />
              GET /api/v1/intersections - List intersections
              <br />
              GET /health - Health check
            </Typography>
          </Box>
          <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              API Gateway (Port 8080)
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              POST /v1/ingest/template - Ingest encrypted template
              <br />
              POST /v1/cases/create - Create operator case
              <br />
              POST /v1/control/issue-token - Issue control token
              <br />
              GET /health - Health check
            </Typography>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  )
}
