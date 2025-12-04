import { useParams } from 'react-router-dom'
import { Box, Paper, Typography, Grid, Chip, Divider, Alert as MuiAlert } from '@mui/material'
import { useAlertStore } from '../store/alertStore'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function Investigation() {
  const { alertId } = useParams<{ alertId: string }>()
  const { alerts } = useAlertStore()

  const alert = alerts.find((a) => a.id === alertId)

  if (!alert) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Investigation
        </Typography>
        <MuiAlert severity="warning">Alert not found</MuiAlert>
      </Box>
    )
  }

  // Mock SHAP values (in production, fetch from API)
  const shapData = [
    { feature: 'bytes_per_second', value: 0.42, impact: 'high' },
    { feature: 'unique_dest_count', value: 0.28, impact: 'medium' },
    { feature: 'packet_variance', value: 0.15, impact: 'medium' },
    { feature: 'protocol_tcp', value: -0.08, impact: 'low' },
    { feature: 'hour_of_day', value: 0.06, impact: 'low' },
    { feature: 'dest_port_443', value: -0.04, impact: 'low' },
  ]

  const getBarColor = (value: number) => {
    return value > 0 ? '#f44336' : '#4caf50'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Threat Investigation
      </Typography>

      {/* Alert Summary */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              {alert.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {alert.description}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Domain
            </Typography>
            <Typography variant="body1">
              <Chip label={alert.domain.toUpperCase()} size="small" variant="outlined" />
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Severity
            </Typography>
            <Typography variant="body1">
              <Chip
                label={alert.severity.toUpperCase()}
                size="small"
                color={
                  alert.severity === 'critical'
                    ? 'error'
                    : alert.severity === 'high'
                    ? 'warning'
                    : 'info'
                }
              />
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Risk Score
            </Typography>
            <Typography variant="h6">{alert.score.toFixed(3)}</Typography>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Confidence
            </Typography>
            <Typography variant="h6">{((alert.confidence || 0) * 100).toFixed(1)}%</Typography>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="caption" color="text.secondary">
              Timestamp
            </Typography>
            <Typography variant="body1">
              {new Date(alert.timestamp).toLocaleString()}
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="caption" color="text.secondary">
              Affected Assets
            </Typography>
            <Box sx={{ mt: 1 }}>
              {alert && alert.affectedAssets && alert.affectedAssets.map((asset, idx) => (
                <Chip key={idx} label={asset} size="small" sx={{ mr: 1, mb: 1 }} />
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* SHAP Explanation */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          AI Explanation (SHAP Feature Importance)
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Features contributing to this prediction. Positive values (red) increase risk, negative
          values (green) decrease it.
        </Typography>

        <Box sx={{ mt: 3 }}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={shapData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="feature" type="category" width={150} />
              <Tooltip />
              <Bar dataKey="value">
                {shapData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.value)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box sx={{ mt: 2 }}>
          {shapData.slice(0, 3).map((feature, idx) => (
            <Box key={idx} sx={{ mb: 1 }}>
              <Typography variant="body2">
                <strong>{feature.feature}:</strong>{' '}
                {feature.value > 0 ? 'Increases' : 'Decreases'} risk by{' '}
                {Math.abs(feature.value).toFixed(2)}
              </Typography>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Recommended Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recommended Actions
        </Typography>
        <MuiAlert severity={alert.severity === 'critical' || alert.severity === 'high' ? 'error' : 'warning'}>
          {alert.action}
        </MuiAlert>

        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" gutterBottom>
            Additional mitigation steps:
          </Typography>
          <ul>
            <li>
              <Typography variant="body2">
                Review activity from affected assets: {alert && alert.affectedAssets ? alert.affectedAssets.join(', ') : 'N/A'}
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Check for similar patterns in historical data (correlation analysis)
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Validate findings with network/security team before taking action
              </Typography>
            </li>
            {alert.severity === 'critical' && (
              <li>
                <Typography variant="body2" color="error">
                  <strong>CRITICAL:</strong> Consider immediate isolation of affected systems
                </Typography>
              </li>
            )}
          </ul>
        </Box>
      </Paper>
    </Box>
  )
}
