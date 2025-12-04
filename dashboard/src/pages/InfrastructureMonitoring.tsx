import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Paper,
  Alert,
  Button,
  CircularProgress,
} from '@mui/material'
import {
  ErrorOutline,
  Phone,
} from '@mui/icons-material'
import { getPipelineStatistics, type PipelineStatistics } from '../api/securityApi'

export default function InfrastructureMonitoring() {
  const [pipelineData, setPipelineData] = useState<PipelineStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      
      const result = await getPipelineStatistics('24h')
      
      if (result.error) {
        setError(result.error)
      } else {
        setPipelineData(result.data ?? null)
      }
      
      setLoading(false)
    }
    
    fetchData()
    const interval = setInterval(fetchData, 60000) // Refresh every 60 seconds
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
        <Alert severity="error">{error}</Alert>
      </Box>
    )
  }

  if (!pipelineData) {
    return (
      <Box p={3}>
        <Alert severity="warning">No pipeline data available</Alert>
      </Box>
    )
  }

  const criticalLeaks = pipelineData.leak_detection.active_leaks
  const radiationAlerts = pipelineData.radiation_monitoring.radiation_alerts
  const environmentalIncidents = pipelineData.environmental_impact.environmental_incidents

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          💧 Pipeline Infrastructure Monitoring
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Real-time pipeline leak detection, radiation monitoring, and predictive maintenance
        </Typography>
      </Box>

      {/* Critical Alerts */}
      {(criticalLeaks > 0 || radiationAlerts > 0 || environmentalIncidents > 0) && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          icon={<ErrorOutline sx={{ fontSize: 32 }} />}
          action={
            <Button color="inherit" size="small" startIcon={<Phone />}>
              CALL EMERGENCY
            </Button>
          }
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            🚨 CRITICAL INFRASTRUCTURE ALERT
          </Typography>
          <Typography>
            {criticalLeaks > 0 && `${criticalLeaks} active pipeline leak(s) detected. `}
            {radiationAlerts > 0 && `${radiationAlerts} radiation alert(s). `}
            {environmentalIncidents > 0 && `${environmentalIncidents} environmental incident(s). `}
            Immediate response required.
          </Typography>
        </Alert>
      )}

      {/* Statistics Dashboard */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>Total Pipelines</Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {pipelineData.pipeline_infrastructure.total_pipelines.toLocaleString()}
              </Typography>
              <Typography variant="caption">
                {pipelineData.pipeline_infrastructure.total_length_km.toLocaleString()} km monitored
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>Active Leaks</Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {pipelineData.leak_detection.active_leaks}
              </Typography>
              <Typography variant="caption">
                {pipelineData.leak_detection.leaks_detected_period} detected this period
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>Radiation Sensors</Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {pipelineData.radiation_monitoring.sensors_active}
              </Typography>
              <Typography variant="caption">
                {radiationAlerts} alerts active
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>Spills Prevented</Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {pipelineData.environmental_impact.spills_prevented}
              </Typography>
              <Typography variant="caption">
                AI-powered prevention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Leak Detection Performance</Typography>
            <Typography variant="body2" color="text.secondary">Detection Time</Typography>
            <Typography variant="h4">{pipelineData.leak_detection.average_detection_time_minutes} min</Typography>
            <Typography variant="caption">False Positive Rate: {pipelineData.leak_detection.false_positive_rate}%</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Predictive Maintenance</Typography>
            <Typography variant="body2" color="text.secondary">Failures Prevented</Typography>
            <Typography variant="h4">{pipelineData.predictive_maintenance.predicted_failures_prevented}</Typography>
            <Typography variant="caption">Maintenance Scheduled: {pipelineData.predictive_maintenance.maintenance_scheduled}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Environmental Impact</Typography>
            <Typography variant="body2" color="text.secondary">Active Cleanup Operations</Typography>
            <Typography variant="h4">{pipelineData.environmental_impact.cleanup_operations_active}</Typography>
            <Typography variant="caption">Incidents: {pipelineData.environmental_impact.environmental_incidents}</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

