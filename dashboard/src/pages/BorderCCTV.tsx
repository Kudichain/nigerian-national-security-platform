import { useState, useEffect } from 'react'
import { Box, Paper, Typography, Grid, Card, CardContent, Chip, Alert, CircularProgress, LinearProgress } from '@mui/material'
import { Videocam, Warning, CheckCircle, LocationOn, People } from '@mui/icons-material'

interface Border {
  id: string
  name: string
  state: string
  country: string
  coordinates: { lat: number; lng: number }
  cameras: number
  online: number
  offline: number
  daily_crossings: number
  vehicles_today: number
  pedestrians_today: number
  alerts: number
  status: string
  last_incident: string
  staff_on_duty: number
}

interface BorderCCTVData {
  total_borders: number
  total_cameras: number
  cameras_online: number
  cameras_offline: number
  total_crossings_today: number
  total_alerts: number
  borders_on_high_alert: number
  borders: Border[]
  operational_status: string
  last_updated: string
}

export default function BorderCCTV() {
  const [data, setData] = useState<BorderCCTVData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchBorderCCTV()
  }, [])

  const fetchBorderCCTV = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/surveillance/border-cctv')
      if (!response.ok) throw new Error('Failed to fetch border CCTV data')
      const result = await response.json()
      setData(result)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch border CCTV data'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'success'
      case 'high_alert': return 'error'
      case 'maintenance': return 'warning'
      default: return 'default'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'operational': return 'Operational'
      case 'high_alert': return 'High Alert'
      case 'maintenance': return 'Maintenance'
      default: return status
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  if (!data) return null

  const operationalRate = ((data.cameras_online / data.total_cameras) * 100).toFixed(1)

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Videocam /> Border CCTV Monitoring
      </Typography>

      {data.borders_on_high_alert > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {data.borders_on_high_alert} border{data.borders_on_high_alert > 1 ? 's' : ''} on high alert!
        </Alert>
      )}

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Borders</Typography>
              <Typography variant="h4">{data.total_borders}</Typography>
              <Typography variant="caption" color="textSecondary">International Crossings</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Cameras</Typography>
              <Typography variant="h4">{data.total_cameras}</Typography>
              <Typography variant="caption" sx={{ color: 'success.main' }}>
                {data.cameras_online} Online • {data.cameras_offline} Offline
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={parseFloat(operationalRate)} 
                sx={{ mt: 1 }}
                color={parseFloat(operationalRate) > 90 ? 'success' : 'warning'}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Crossings Today</Typography>
              <Typography variant="h4">{data.total_crossings_today.toLocaleString()}</Typography>
              <Typography variant="caption" color="textSecondary">
                Vehicles & Pedestrians
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Active Alerts</Typography>
              <Typography variant="h4" sx={{ color: data.total_alerts > 10 ? 'error.main' : 'warning.main' }}>
                {data.total_alerts}
              </Typography>
              <Typography variant="caption" color="textSecondary">Security Incidents</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Border Details */}
      <Grid container spacing={3}>
        {data.borders.map((border) => (
          <Grid item xs={12} md={6} key={border.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6">{border.name}</Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <LocationOn fontSize="small" /> {border.state} • Border with {border.country}
                    </Typography>
                  </Box>
                  <Chip 
                    label={getStatusLabel(border.status)} 
                    color={getStatusColor(border.status) as 'success' | 'warning' | 'error'}
                    size="small"
                    icon={border.status === 'operational' ? <CheckCircle /> : <Warning />}
                  />
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1.5, bgcolor: 'background.default' }}>
                      <Typography variant="caption" color="textSecondary">Cameras</Typography>
                      <Typography variant="h6">
                        {border.online}/{border.cameras}
                      </Typography>
                      <Typography variant="caption" sx={{ color: border.offline > 0 ? 'error.main' : 'success.main' }}>
                        {border.offline > 0 ? `${border.offline} Offline` : 'All Online'}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1.5, bgcolor: 'background.default' }}>
                      <Typography variant="caption" color="textSecondary">Crossings Today</Typography>
                      <Typography variant="h6">{border.daily_crossings.toLocaleString()}</Typography>
                      <Typography variant="caption" color="textSecondary">
                        Total Traffic
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1.5, bgcolor: 'background.default' }}>
                      <Typography variant="caption" color="textSecondary">Vehicles</Typography>
                      <Typography variant="h6">{border.vehicles_today.toLocaleString()}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1.5, bgcolor: 'background.default' }}>
                      <Typography variant="caption" color="textSecondary">Pedestrians</Typography>
                      <Typography variant="h6">{border.pedestrians_today.toLocaleString()}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1.5, bgcolor: 'background.default' }}>
                      <Typography variant="caption" color="textSecondary">Staff on Duty</Typography>
                      <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <People fontSize="small" /> {border.staff_on_duty}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1.5, bgcolor: border.alerts > 5 ? 'error.dark' : 'background.default' }}>
                      <Typography variant="caption" color="textSecondary">Alerts</Typography>
                      <Typography variant="h6" sx={{ color: border.alerts > 5 ? 'error.light' : 'inherit' }}>
                        {border.alerts}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {border.alerts > 0 && (
                  <Alert severity={border.alerts > 5 ? 'error' : 'warning'} sx={{ mt: 2 }}>
                    {border.alerts} active security alert{border.alerts > 1 ? 's' : ''} at this border
                  </Alert>
                )}

                <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                  Last Incident: {new Date(border.last_incident).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
