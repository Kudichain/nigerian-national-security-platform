import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Stack,
  Paper,
  CircularProgress,
  Alert as MuiAlert,
} from '@mui/material'
import {
  Videocam,
  Flight,
  Warning,
  CheckCircle,
} from '@mui/icons-material'
import { getRailwayStatistics, getImmigrationStatistics, type RailwayStatistics, type ImmigrationStatistics } from '../api/securityApi'

export default function CCTVMonitoring() {
  const [railwayData, setRailwayData] = useState<RailwayStatistics | null>(null)
  const [immigrationData, setImmigrationData] = useState<ImmigrationStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      
      const [railwayRes, immigrationRes] = await Promise.all([
        getRailwayStatistics('24h'),
        getImmigrationStatistics(undefined, '24h')
      ])
      
      if (railwayRes.error || immigrationRes.error) {
        setError(railwayRes.error || immigrationRes.error || 'Failed to fetch data')
      } else {
        setRailwayData(railwayRes.data ?? null)
        setImmigrationData(immigrationRes.data ?? null)
      }
      
      setLoading(false)
    }
    
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    )
  }

  if (error) {
    return (
      <Box p={3}>
        <MuiAlert severity="error">{error}</MuiAlert>
      </Box>
    )
  }

  if (!railwayData || !immigrationData) {
    return (
      <Box p={3}>
        <MuiAlert severity="warning">No CCTV data available</MuiAlert>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Videocam /> CCTV & Security Monitoring
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Real-time surveillance feeds from railway stations and airports
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {railwayData.cctv_monitoring.cameras_total.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Railway Cameras
                  </Typography>
                </Box>
                <Videocam sx={{ fontSize: 48, opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {railwayData.cctv_monitoring.cameras_operational.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Cameras Online
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 48, opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {railwayData.threat_detection.suspicious_activities_flagged}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Threat Detections
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 48, opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 700 }}>
                    {immigrationData.airport_operations.terminals_operational}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Airport Terminals
                  </Typography>
                </Box>
                <Flight sx={{ fontSize: 48, opacity: 0.3 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Railway Security Metrics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Railway Operations</Typography>
            <Typography variant="body2" color="text.secondary">Trains Tracked</Typography>
            <Typography variant="h4">{railwayData.train_operations.trains_tracked}</Typography>
            <Typography variant="caption">On-Time Performance: {railwayData.train_operations.on_time_performance_percent}%</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Station Security
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Stations Monitored
            </Typography>
            <Typography variant="h4">
              {railwayData.station_security.stations_monitored}
            </Typography>
            <Typography variant="caption">
              Security Officers: {railwayData.station_security.security_officers}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Airport Security</Typography>
            <Typography variant="body2" color="text.secondary">Passengers Processed (24h)</Typography>
            <Typography variant="h4">{immigrationData.passenger_processing.passengers_processed_period.toLocaleString()}</Typography>
            <Typography variant="caption">Average Time: {immigrationData.passenger_processing.average_processing_time_minutes} min</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>AI Threat Detection</Typography>
            <Typography variant="body2" color="text.secondary">Response Time</Typography>
            <Typography variant="h4">{railwayData.threat_detection.average_response_time_seconds}s</Typography>
            <Typography variant="caption">False Positive Rate: {railwayData.threat_detection.false_positive_rate}%</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Risk Assessment</Typography>
            <Typography variant="body2" color="text.secondary">High Risk Passengers Flagged</Typography>
            <Typography variant="h4">{immigrationData.risk_assessment.high_risk_passengers}</Typography>
            <Typography variant="caption">Secondary Screenings: {immigrationData.risk_assessment.secondary_screenings}</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
