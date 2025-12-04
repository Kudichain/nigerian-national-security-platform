import { useState, useEffect } from 'react'
import { Box, Paper, Typography, Grid, Card, CardContent, Chip, Alert, CircularProgress, LinearProgress, TextField, MenuItem } from '@mui/material'
import { Traffic, AttachMoney, LocationOn } from '@mui/icons-material'

interface State {
  name: string
  capital: string
  zone: string
  tollgates: number
  cameras: number
  online: number
  offline: number
  vehicles_today: number
  operational_rate: number
  revenue_today: number
  alerts: number
}

interface TollgateCCTVData {
  total_states: number
  total_tollgates: number
  total_cameras: number
  cameras_online: number
  cameras_offline: number
  total_vehicles_today: number
  total_revenue_today: number
  total_alerts: number
  operational_rate: number
  states: State[]
  zones: { [key: string]: number }
  last_updated: string
}

export default function TollgateCCTV() {
  const [data, setData] = useState<TollgateCCTVData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedZone, setSelectedZone] = useState('All')

  useEffect(() => {
    fetchTollgateCCTV()
  }, [])

  const fetchTollgateCCTV = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/surveillance/tollgate-cctv')
      if (!response.ok) throw new Error('Failed to fetch tollgate CCTV data')
      const result = await response.json()
      setData(result)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tollgate CCTV data'
      setError(errorMessage)
    } finally {
      setLoading(false)
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

  const filteredStates = selectedZone === 'All' 
    ? data.states 
    : data.states.filter(s => s.zone === selectedZone)

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const getOperationalColor = (rate: number) => {
    if (rate >= 95) return 'success'
    if (rate >= 85) return 'warning'
    return 'error'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Traffic /> Toll Gate CCTV Monitoring
      </Typography>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total States</Typography>
              <Typography variant="h4">{data.total_states}</Typography>
              <Typography variant="caption" color="textSecondary">{data.total_tollgates} Toll Gates</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Total Cameras</Typography>
              <Typography variant="h4">{data.total_cameras}</Typography>
              <Typography variant="caption" sx={{ color: 'success.main' }}>
                {data.cameras_online} Online
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={data.operational_rate} 
                sx={{ mt: 1 }}
                color={data.operational_rate > 90 ? 'success' : 'warning'}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ bgcolor: 'primary.dark' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Vehicles Today</Typography>
              <Typography variant="h4">{data.total_vehicles_today.toLocaleString()}</Typography>
              <Typography variant="caption" color="textSecondary">Across All Gates</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ bgcolor: 'success.dark' }}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Revenue Today</Typography>
              <Typography variant="h5">{formatCurrency(data.total_revenue_today)}</Typography>
              <Typography variant="caption" color="textSecondary">Collection</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>Active Alerts</Typography>
              <Typography variant="h4" sx={{ color: data.total_alerts > 20 ? 'error.main' : 'warning.main' }}>
                {data.total_alerts}
              </Typography>
              <Typography variant="caption" color="textSecondary">Incidents</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Zone Filter */}
      <Box sx={{ mb: 3 }}>
        <TextField
          select
          label="Filter by Zone"
          value={selectedZone}
          onChange={(e) => setSelectedZone(e.target.value)}
          sx={{ minWidth: 250 }}
        >
          <MenuItem value="All">All Zones ({data.total_states})</MenuItem>
          {Object.entries(data.zones).map(([zone, count]) => (
            <MenuItem key={zone} value={zone}>{zone} ({count})</MenuItem>
          ))}
        </TextField>
      </Box>

      {/* States Grid */}
      <Grid container spacing={2}>
        {filteredStates.map((state) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={state.name}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                  <Box>
                    <Typography variant="h6">{state.name}</Typography>
                    <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <LocationOn fontSize="small" /> {state.capital}
                    </Typography>
                  </Box>
                  <Chip 
                    label={state.zone.split(' ')[0]} 
                    size="small"
                    color={
                      state.zone.includes('South') ? 'primary' : 
                      state.zone.includes('North') ? 'secondary' : 'default'
                    }
                  />
                </Box>

                <Box sx={{ my: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption" color="textSecondary">Operational Rate</Typography>
                    <Typography variant="caption" fontWeight="bold">{state.operational_rate}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={state.operational_rate} 
                    color={getOperationalColor(state.operational_rate) as 'success' | 'warning' | 'error'}
                  />
                </Box>

                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1, bgcolor: 'background.default', textAlign: 'center' }}>
                      <Typography variant="caption" color="textSecondary">Toll Gates</Typography>
                      <Typography variant="body1" fontWeight="bold">{state.tollgates}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 1, bgcolor: 'background.default', textAlign: 'center' }}>
                      <Typography variant="caption" color="textSecondary">Cameras</Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {state.online}/{state.cameras}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12}>
                    <Paper sx={{ p: 1, bgcolor: 'primary.dark', textAlign: 'center' }}>
                      <Typography variant="caption" color="textSecondary">Vehicles Today</Typography>
                      <Typography variant="body1" fontWeight="bold">{state.vehicles_today.toLocaleString()}</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12}>
                    <Paper sx={{ p: 1, bgcolor: 'success.dark', textAlign: 'center' }}>
                      <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <AttachMoney fontSize="small" /> Revenue Today
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">{formatCurrency(state.revenue_today)}</Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {state.alerts > 0 && (
                  <Alert severity="warning" sx={{ mt: 1.5, py: 0.5 }}>
                    <Typography variant="caption">
                      {state.alerts} active alert{state.alerts > 1 ? 's' : ''}
                    </Typography>
                  </Alert>
                )}

                {state.offline > 0 && (
                  <Alert severity="error" sx={{ mt: 1, py: 0.5 }}>
                    <Typography variant="caption">
                      {state.offline} camera{state.offline > 1 ? 's' : ''} offline
                    </Typography>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="caption" color="textSecondary" sx={{ mt: 3, display: 'block' }}>
        Last Updated: {new Date(data.last_updated).toLocaleString()}
      </Typography>
    </Box>
  )
}
