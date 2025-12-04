/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from 'react'
import { Box, Paper, Typography, TextField, Button, Grid, Card, CardContent, Avatar, Chip, CircularProgress, Alert } from '@mui/material'
import { Phone, LocationOn, Search } from '@mui/icons-material'

export default function PhoneTracking() {
  const [phoneNumber, setPhoneNumber] = useState('')
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<Record<string, any> | null>(null)
  const [loading, setLoading] = useState(false)

  const handleVerify = async () => {
    if (!phoneNumber) return
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/phone/verify?phone_number=' + encodeURIComponent(phoneNumber), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ error: 'Failed to verify phone. Please ensure service is running.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Phone sx={{ fontSize: 40 }} /> Phone Number Tracking
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Real-time phone verification and location tracking system
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Phone Number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+234XXXXXXXXXX"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handleVerify}
              disabled={!phoneNumber || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Search />}
              sx={{ height: '100%' }}
            >
              {loading ? 'Tracking...' : 'Verify & Track'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {result && !loading && (
        <Paper sx={{ p: 3 }}>
          {result.error ? (
            <Alert severity="error">{result.error}</Alert>
          ) : result.registered ? (
            <Grid container spacing={3}>
              {/* Owner Info */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Owner Information</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Avatar src={result.owner.photo} sx={{ width: 64, height: 64 }} />
                      <Box>
                        <Typography variant="h6">{result.owner.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          NIN: {result.owner.nin}
                        </Typography>
                      </Box>
                    </Box>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">Carrier</Typography>
                        <Typography variant="body2">{result.owner.carrier}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">SIM Status</Typography>
                        <Chip label={result.owner.sim_status} size="small" color="success" />
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="caption" color="text.secondary">Registered</Typography>
                        <Typography variant="body2">{result.owner.registered_date}</Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Location */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LocationOn /> Real-Time Location
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      📍 {result.location.current}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {result.location.coordinates.latitude}, {result.location.coordinates.longitude}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Last seen: {result.location.last_seen}
                    </Typography>
                    <Typography variant="caption" display="block" color="text.secondary">
                      Cell tower: {result.location.cell_tower}
                    </Typography>

                    <Typography variant="subtitle2" sx={{ mt: 2 }}>Location History</Typography>
                    {result.location.history.map((loc: any, i: number) => (
                      <Typography key={i} variant="body2" color="text.secondary">
                        • {loc.location} ({loc.duration})
                      </Typography>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              {/* Activity */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Activity Today</Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light' }}>
                          <Typography variant="h4">{result.activity.calls_today}</Typography>
                          <Typography variant="caption">Calls</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'secondary.light' }}>
                          <Typography variant="h4">{result.activity.sms_today}</Typography>
                          <Typography variant="caption">SMS</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light' }}>
                          <Typography variant="h4">{result.activity.data_usage_mb}MB</Typography>
                          <Typography variant="caption">Data</Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: result.activity.roaming ? 'warning.light' : 'info.light' }}>
                          <Typography variant="body1">{result.activity.roaming ? 'Yes' : 'No'}</Typography>
                          <Typography variant="caption">Roaming</Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Warnings */}
              {result.warnings && result.warnings.length > 0 && (
                <Grid item xs={12}>
                  <Alert severity="warning">
                    <Typography variant="subtitle2">⚠️ Warnings:</Typography>
                    {result.warnings.map((warning: string, i: number) => (
                      <Typography key={i} variant="body2">• {warning}</Typography>
                    ))}
                  </Alert>
                </Grid>
              )}
            </Grid>
          ) : (
            <Alert severity="warning">Phone number not registered</Alert>
          )}
        </Paper>
      )}
    </Box>
  )
}
