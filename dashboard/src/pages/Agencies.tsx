import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from '@mui/material'
import {
  HowToVote,
  LocalFireDepartment,
  LocalPolice,
  Forum,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Refresh,
} from '@mui/icons-material'

type ServiceStatus = {
  name: string
  port: number
  status: 'healthy' | 'error' | 'unknown'
  icon: React.ReactNode
  color: string
  stats?: ServiceMetrics | null
}

type ServiceMetrics = Record<string, number | string | boolean | null | undefined>

type ServiceHealth = {
  status: ServiceStatus['status']
  stats: ServiceMetrics | null
}

export default function Agencies() {
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      name: 'INEC Voter Verification',
      port: 8085,
      status: 'unknown',
      icon: <HowToVote />,
      color: '#4caf50',
    },
    {
      name: 'Federal Fire Service',
      port: 8086,
      status: 'unknown',
      icon: <LocalFireDepartment />,
      color: '#ff5722',
    },
    {
      name: 'Nigeria Police Force',
      port: 8087,
      status: 'unknown',
      icon: <LocalPolice />,
      color: '#2196f3',
    },
    {
      name: 'Social Media Regulation',
      port: 8088,
      status: 'unknown',
      icon: <Forum />,
      color: '#9c27b0',
    },
  ])

  const [selectedService, setSelectedService] = useState<string | null>(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [loading, setLoading] = useState(false)

  const servicesRef = useRef<ServiceStatus[]>(services)

  useEffect(() => {
    servicesRef.current = services
  }, [services])

  const checkServiceHealth = useCallback(async (port: number): Promise<ServiceHealth> => {
    const endpoints: Record<number, string> = {
      8085: 'http://localhost:8000/api/v1/inec/health',
      8086: 'http://localhost:8000/api/v1/fire/health',
      8087: 'http://localhost:8000/api/v1/police/health',
      8088: 'http://localhost:8000/api/v1/social/health',
    }

    const endpoint = endpoints[port]
    if (!endpoint) {
      return { status: 'unknown', stats: null }
    }

    try {
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: { Accept: 'application/json' },
      })
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      const data = (await response.json()) as ServiceMetrics
      return { status: 'healthy', stats: data }
    } catch (error) {
      console.error('Service health check failed:', error)
      return { status: 'error', stats: null }
    }
  }, [])

  const refreshAllServices = useCallback(async () => {
    setLoading(true)
    try {
      const updated = await Promise.all(
        servicesRef.current.map(async (service) => {
          const health = await checkServiceHealth(service.port)
          return { ...service, status: health.status, stats: health.stats }
        })
      )
      setServices(updated)
    } finally {
      setLoading(false)
    }
  }, [checkServiceHealth])

  useEffect(() => {
    void refreshAllServices()
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      void refreshAllServices()
    }, 30000)
    return () => clearInterval(interval)
  }, [refreshAllServices])

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Government Agency Integrations</Typography>
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
          onClick={refreshAllServices}
          disabled={loading}
        >
          Refresh Status
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {services.map((service) => (
          <Grid item xs={12} sm={6} md={3} key={service.port}>
            <Card
              sx={{
                cursor: 'pointer',
                '&:hover': { boxShadow: 6 },
                borderLeft: `4px solid ${service.color}`,
              }}
              onClick={() => {
                setSelectedService(service.name)
                setOpenDialog(true)
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{ color: service.color }}>{service.icon}</Box>
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {service.name}
                  </Typography>
                  {service.status === 'healthy' ? (
                    <CheckCircle color="success" />
                  ) : service.status === 'error' ? (
                    <ErrorIcon color="error" />
                  ) : (
                    <Warning color="warning" />
                  )}
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Port: {service.port}
                </Typography>
                <Chip
                  label={service.status.toUpperCase()}
                  size="small"
                  color={service.status === 'healthy' ? 'success' : service.status === 'error' ? 'error' : 'default'}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* INEC Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <HowToVote sx={{ verticalAlign: 'middle', mr: 1 }} />
          INEC - Voter Verification
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Privacy-preserving voter verification, polling unit assistance, queue management
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Verifications
              </Typography>
              <Typography variant="h4">
                {services[0]?.stats?.total_verifications || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Pending Reviews
              </Typography>
              <Typography variant="h4">
                {services[0]?.stats?.pending_reviews || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Polling Units
              </Typography>
              <Typography variant="h4">2</Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Fire Service Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <LocalFireDepartment sx={{ verticalAlign: 'middle', mr: 1 }} />
          Federal Fire Service
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Automated fire/smoke detection, GPS alerting, emergency response coordination
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Active Incidents
              </Typography>
              <Typography variant="h4" color="error">
                {services[1]?.stats?.active_incidents || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Incidents
              </Typography>
              <Typography variant="h4">
                {services[1]?.stats?.total_incidents || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Notifications Sent
              </Typography>
              <Typography variant="h4">
                {services[1]?.stats?.notifications_sent || 0}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Police Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <LocalPolice sx={{ verticalAlign: 'middle', mr: 1 }} />
          Nigeria Police Force
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Security threat detection, analyst review, rapid response coordination
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Pending Reviews
              </Typography>
              <Typography variant="h4" color="warning">
                {services[2]?.stats?.pending_analyst_review || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Active Incidents
              </Typography>
              <Typography variant="h4">
                {services[2]?.stats?.active_incidents || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Incidents
              </Typography>
              <Typography variant="h4">
                {services[2]?.stats?.total_incidents || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Dispatches Today
              </Typography>
              <Typography variant="h4">
                {services[2]?.stats?.dispatches_today || 0}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Social Media Section */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          <Forum sx={{ verticalAlign: 'middle', mr: 1 }} />
          Social Media Regulation
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Content moderation, Cybercrime Act compliance, law enforcement reporting
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(156, 39, 176, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Pending Reviews
              </Typography>
              <Typography variant="h4" color="secondary">
                {services[3]?.stats?.pending_reviews || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Records
              </Typography>
              <Typography variant="h4">
                {services[3]?.stats?.total_records || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Law Enforcement Reports
              </Typography>
              <Typography variant="h4">
                {services[3]?.stats?.law_enforcement_reports || 0}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Compliance Rate
              </Typography>
              <Typography variant="h4">98%</Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Service Details Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedService}</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Service running on port {services.find((s) => s.name === selectedService)?.port}
          </Alert>
          <Typography variant="body2" paragraph>
            Use the API endpoints below to interact with this service.
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Endpoint</TableCell>
                  <TableCell>Method</TableCell>
                  <TableCell>Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {selectedService === 'INEC Voter Verification' && (
                  <>
                    <TableRow>
                      <TableCell>/api/v1/verify</TableCell>
                      <TableCell>POST</TableCell>
                      <TableCell>Verify voter registration</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>/api/v1/polling-units</TableCell>
                      <TableCell>GET</TableCell>
                      <TableCell>List polling units</TableCell>
                    </TableRow>
                  </>
                )}
                {selectedService === 'Federal Fire Service' && (
                  <>
                    <TableRow>
                      <TableCell>/api/v1/detect</TableCell>
                      <TableCell>POST</TableCell>
                      <TableCell>Report fire detection</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>/api/v1/incidents</TableCell>
                      <TableCell>GET</TableCell>
                      <TableCell>List incidents</TableCell>
                    </TableRow>
                  </>
                )}
                {selectedService === 'Nigeria Police Force' && (
                  <>
                    <TableRow>
                      <TableCell>/api/v1/alerts</TableCell>
                      <TableCell>POST</TableCell>
                      <TableCell>Submit security alert</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>/api/v1/incidents</TableCell>
                      <TableCell>GET</TableCell>
                      <TableCell>List incidents (pending review)</TableCell>
                    </TableRow>
                  </>
                )}
                {selectedService === 'Social Media Regulation' && (
                  <>
                    <TableRow>
                      <TableCell>/api/v1/moderate</TableCell>
                      <TableCell>POST</TableCell>
                      <TableCell>Submit content for moderation</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>/api/v1/compliance/report</TableCell>
                      <TableCell>GET</TableCell>
                      <TableCell>Get compliance report</TableCell>
                    </TableRow>
                  </>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
