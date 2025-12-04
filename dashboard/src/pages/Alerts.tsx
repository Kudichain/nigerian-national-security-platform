import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material'
import type { ChipProps } from '@mui/material'
import { DataGrid, GridColDef } from '@mui/x-data-grid'
import { Visibility as ViewIcon } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useAlertStore, Alert } from '../store/alertStore'

export default function Alerts() {
  const navigate = useNavigate()
  const { alerts, updateAlert } = useAlertStore()
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<string>('all')
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null)

  // Filter alerts
  const filteredAlerts = alerts.filter((alert) => {
    if (selectedDomain !== 'all' && alert.domain !== selectedDomain) return false
    if (selectedSeverity !== 'all' && alert.severity !== selectedSeverity) return false
    if (selectedStatus !== 'all' && alert.status !== selectedStatus) return false
    return true
  })

  const getSeverityColor = (severity: Alert['severity']): ChipProps['color'] => {
    switch (severity) {
      case 'critical':
        return 'error'
      case 'high':
        return 'warning'
      case 'medium':
        return 'info'
      case 'low':
        return 'success'
      default:
        return 'default'
    }
  }

  const columns: GridColDef[] = [
    {
      field: 'timestamp',
      headerName: 'Time',
      width: 180,
      valueFormatter: (params) => new Date(params.value as string).toLocaleString(),
    },
    {
      field: 'domain',
      headerName: 'Domain',
      width: 120,
      renderCell: (params) => (
        <Chip label={params.value.toUpperCase()} size="small" variant="outlined" />
      ),
    },
    {
      field: 'severity',
      headerName: 'Severity',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value.toUpperCase()}
          size="small"
              color={getSeverityColor(params.value as Alert['severity'])}
        />
      ),
    },
    {
      field: 'title',
      headerName: 'Alert',
      flex: 1,
      minWidth: 250,
    },
    {
      field: 'score',
      headerName: 'Score',
      width: 100,
      valueFormatter: (params) => (params.value as number).toFixed(2),
    },
    {
      field: 'confidence',
      headerName: 'Confidence',
      width: 120,
      valueFormatter: (params) => `${((params.value as number) * 100).toFixed(1)}%`,
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 140,
      renderCell: (params) => (
        <FormControl size="small" fullWidth>
          <Select
            value={params.value}
                onChange={(event) =>
                  updateAlert(params.row.id, {
                    status: event.target.value as Alert['status'],
                  })
                }
            variant="standard"
          >
            <MenuItem value="new">New</MenuItem>
            <MenuItem value="investigating">Investigating</MenuItem>
            <MenuItem value="resolved">Resolved</MenuItem>
            <MenuItem value="false_positive">False Positive</MenuItem>
          </Select>
        </FormControl>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      sortable: false,
      renderCell: (params) => (
        <IconButton
          size="small"
          onClick={() => {
            setSelectedAlert(params.row as Alert)
            setDetailsOpen(true)
          }}
        >
          <ViewIcon />
        </IconButton>
      ),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Alerts
      </Typography>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Domain</InputLabel>
            <Select
              value={selectedDomain}
              label="Domain"
              onChange={(e) => setSelectedDomain(e.target.value)}
            >
              <MenuItem value="all">All Domains</MenuItem>
              <MenuItem value="nids">NIDS</MenuItem>
              <MenuItem value="logs">Logs</MenuItem>
              <MenuItem value="phishing">Phishing</MenuItem>
              <MenuItem value="auth">Auth</MenuItem>
              <MenuItem value="malware">Malware</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Severity</InputLabel>
            <Select
              value={selectedSeverity}
              label="Severity"
              onChange={(e) => setSelectedSeverity(e.target.value)}
            >
              <MenuItem value="all">All Severities</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={selectedStatus}
              label="Status"
              onChange={(e) => setSelectedStatus(e.target.value)}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="new">New</MenuItem>
              <MenuItem value="investigating">Investigating</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
              <MenuItem value="false_positive">False Positive</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Alerts Table */}
      <Paper sx={{ height: 600 }}>
        <DataGrid
          rows={filteredAlerts}
          columns={columns}
          pageSizeOptions={[25, 50, 100]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } },
          }}
          disableRowSelectionOnClick
        />
      </Paper>

      {/* Alert Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedAlert && (
          <>
            <DialogTitle>
              Alert Details: {selectedAlert.title}
            </DialogTitle>
            <DialogContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
                <Typography>
                  <strong>Domain:</strong> {selectedAlert.domain.toUpperCase()}
                </Typography>
                <Typography>
                  <strong>Severity:</strong>{' '}
                  <Chip
                    label={selectedAlert.severity.toUpperCase()}
                    size="small"
                    color={getSeverityColor(selectedAlert.severity)}
                  />
                </Typography>
                <Typography>
                  <strong>Time:</strong> {new Date(selectedAlert.timestamp).toLocaleString()}
                </Typography>
                <Typography>
                  <strong>Score:</strong> {selectedAlert.score.toFixed(3)}
                </Typography>
                <Typography>
                  <strong>Confidence:</strong> {((selectedAlert.confidence || 0) * 100).toFixed(1)}%
                </Typography>
                <Typography>
                  <strong>Description:</strong> {selectedAlert.description}
                </Typography>
                <Typography>
                  <strong>Recommended Action:</strong> {selectedAlert.action}
                </Typography>
                <Box>
                  <Typography gutterBottom>
                    <strong>Affected Assets:</strong>
                  </Typography>
                  {(selectedAlert.affectedAssets || []).map((asset, idx) => (
                    <Chip key={idx} label={asset} size="small" sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsOpen(false)}>Close</Button>
              <Button
                variant="contained"
                onClick={() => {
                  navigate(`/investigation/${selectedAlert.id}`)
                  setDetailsOpen(false)
                }}
              >
                Investigate
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}
