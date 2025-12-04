import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  Chip,
} from '@mui/material'
import { Upload as UploadIcon, PlayArrow as TrainIcon, Delete as DeleteIcon } from '@mui/icons-material'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index } = props
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Settings() {
  const [tabValue, setTabValue] = useState(0)
  const [thresholds, setThresholds] = useState({
    nids: 0.7,
    logs: 0.75,
    phishing: 0.8,
    auth: 0.65,
    malware: 0.9,
  })

  const trustedEntities = [
    { id: 1, type: 'IP', value: '192.168.1.100', addedBy: 'admin', date: '2024-01-15' },
    { id: 2, type: 'Domain', value: 'trusted-partner.com', addedBy: 'admin', date: '2024-01-10' },
    { id: 3, type: 'Email', value: 'vendor@example.com', addedBy: 'analyst', date: '2024-01-08' },
  ]

  const modelVersions = [
    { domain: 'nids', current: 'v2.3.1', available: ['v2.3.1', 'v2.2.0', 'v2.1.5'], status: 'active' },
    { domain: 'logs', current: 'v1.8.2', available: ['v1.8.2', 'v1.8.1', 'v1.7.0'], status: 'active' },
    { domain: 'phishing', current: 'v3.0.0', available: ['v3.0.0', 'v2.9.5'], status: 'active' },
    { domain: 'auth', current: 'v1.5.3', available: ['v1.5.3', 'v1.5.2'], status: 'active' },
    { domain: 'malware', current: 'v2.1.0', available: ['v2.1.0', 'v2.0.8'], status: 'active' },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Paper>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Thresholds" />
          <Tab label="Trusted Entities" />
          <Tab label="Model Management" />
          <Tab label="Training" />
        </Tabs>

        {/* Thresholds Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Alert Thresholds
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Adjust confidence thresholds for each domain. Higher values reduce false positives but
            may miss threats.
          </Typography>

          <Grid container spacing={4}>
            {Object.entries(thresholds).map(([domain, value]) => (
              <Grid item xs={12} md={6} key={domain}>
                <Box sx={{ px: 2 }}>
                  <Typography gutterBottom>
                    {domain.toUpperCase()} - {(value * 100).toFixed(0)}%
                  </Typography>
                  <Slider
                    value={value}
                    onChange={(_, newValue) =>
                      setThresholds({ ...thresholds, [domain]: newValue as number })
                    }
                    min={0.5}
                    max={0.95}
                    step={0.05}
                    marks={[
                      { value: 0.5, label: '50%' },
                      { value: 0.7, label: '70%' },
                      { value: 0.9, label: '90%' },
                    ]}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(val) => `${(val * 100).toFixed(0)}%`}
                  />
                </Box>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button variant="contained">Save Changes</Button>
            <Button variant="outlined">Reset to Defaults</Button>
          </Box>
        </TabPanel>

        {/* Trusted Entities Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Trusted Entities Whitelist
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            IPs, domains, and emails that should bypass certain security checks.
          </Typography>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select label="Type" defaultValue="IP">
                  <MenuItem value="IP">IP Address</MenuItem>
                  <MenuItem value="Domain">Domain</MenuItem>
                  <MenuItem value="Email">Email</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField fullWidth label="Value" placeholder="e.g., 192.168.1.50" />
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button variant="contained" fullWidth sx={{ height: '56px' }}>
                Add
              </Button>
            </Grid>
          </Grid>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Added By</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {trustedEntities.map((entity) => (
                  <TableRow key={entity.id}>
                    <TableCell>
                      <Chip label={entity.type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{entity.value}</TableCell>
                    <TableCell>{entity.addedBy}</TableCell>
                    <TableCell>{entity.date}</TableCell>
                    <TableCell>
                      <IconButton size="small" color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        {/* Model Management Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Model Version Control
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Manage and deploy different versions of ML models.
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Domain</TableCell>
                  <TableCell>Current Version</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Available Versions</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {modelVersions.map((model) => (
                  <TableRow key={model.domain}>
                    <TableCell>
                      <Chip label={model.domain.toUpperCase()} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{model.current}</TableCell>
                    <TableCell>
                      <Chip label={model.status} size="small" color="success" />
                    </TableCell>
                    <TableCell>
                      <FormControl size="small" sx={{ minWidth: 150 }}>
                        <Select value={model.current}>
                          {model.available.map((version) => (
                            <MenuItem key={version} value={version}>
                              {version}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </TableCell>
                    <TableCell>
                      <Button size="small" variant="outlined">
                        Deploy
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Alert severity="info" sx={{ mt: 3 }}>
            Models are automatically versioned in MLflow. Deploying a new version will update the
            inference service.
          </Alert>
        </TabPanel>

        {/* Training Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Model Training & Retraining
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Upload new datasets or retrain models with current data.
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper variant="outlined" sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Upload Training Data
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Domain</InputLabel>
                  <Select label="Domain" defaultValue="nids">
                    <MenuItem value="nids">NIDS</MenuItem>
                    <MenuItem value="logs">Logs</MenuItem>
                    <MenuItem value="phishing">Phishing</MenuItem>
                    <MenuItem value="auth">Auth</MenuItem>
                    <MenuItem value="malware">Malware</MenuItem>
                  </Select>
                </FormControl>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<UploadIcon />}
                  component="label"
                >
                  Upload Dataset (CSV/Parquet)
                  <input type="file" hidden accept=".csv,.parquet" />
                </Button>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper variant="outlined" sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Trigger Retraining
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Domain</InputLabel>
                  <Select label="Domain" defaultValue="nids">
                    <MenuItem value="nids">NIDS</MenuItem>
                    <MenuItem value="logs">Logs</MenuItem>
                    <MenuItem value="phishing">Phishing</MenuItem>
                    <MenuItem value="auth">Auth</MenuItem>
                    <MenuItem value="malware">Malware</MenuItem>
                  </Select>
                </FormControl>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Use drift-detected samples"
                  sx={{ mb: 2 }}
                />
                <Button variant="contained" fullWidth startIcon={<TrainIcon />}>
                  Start Training
                </Button>
              </Paper>
            </Grid>
          </Grid>

          <Alert severity="warning" sx={{ mt: 3 }}>
            Training jobs run asynchronously. Monitor progress in MLflow UI or check logs.
          </Alert>
        </TabPanel>
      </Paper>
    </Box>
  )
}
