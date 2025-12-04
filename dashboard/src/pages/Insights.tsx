import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
} from '@mui/material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Insights() {
  const [selectedDomain, setSelectedDomain] = useState('nids')
  const [tabValue, setTabValue] = useState(0)

  // Mock data - in production, fetch from backend
  const trendData = Array.from({ length: 30 }, (_, i) => ({
    day: `Day ${i + 1}`,
    alerts: Math.floor(Math.random() * 50) + 20,
    avgScore: Math.random() * 0.5 + 0.5,
    falsePositives: Math.floor(Math.random() * 5),
  }))

  const featureImportance = [
    { feature: 'bytes_per_sec', importance: 0.28 },
    { feature: 'unique_dests', importance: 0.22 },
    { feature: 'packet_variance', importance: 0.18 },
    { feature: 'protocol_type', importance: 0.12 },
    { feature: 'time_of_day', importance: 0.10 },
    { feature: 'port_number', importance: 0.10 },
  ]

  const performanceMetrics = [
    { metric: 'Precision', value: 0.92 },
    { metric: 'Recall', value: 0.88 },
    { metric: 'F1-Score', value: 0.90 },
    { metric: 'Accuracy', value: 0.94 },
    { metric: 'AUC-ROC', value: 0.96 },
  ]

  const entityRiskScores = [
    { entity: '192.168.1.105', risk: 0.89, category: 'High' },
    { entity: '192.168.1.203', risk: 0.76, category: 'Medium' },
    { entity: 'user@company.com', risk: 0.68, category: 'Medium' },
    { entity: '10.0.5.42', risk: 0.54, category: 'Low' },
    { entity: 'admin@company.com', risk: 0.32, category: 'Low' },
  ]

  const anomalyPatterns = [
    { pattern: 'Port Scanning', occurrences: 45, avgSeverity: 'High' },
    { pattern: 'Brute Force', occurrences: 32, avgSeverity: 'Critical' },
    { pattern: 'Data Exfiltration', occurrences: 12, avgSeverity: 'Critical' },
    { pattern: 'Lateral Movement', occurrences: 8, avgSeverity: 'High' },
    { pattern: 'Privilege Escalation', occurrences: 5, avgSeverity: 'Critical' },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI Insights & Analytics
      </Typography>

      {/* Domain Selector */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select Domain</InputLabel>
          <Select
            value={selectedDomain}
            label="Select Domain"
            onChange={(e) => setSelectedDomain(e.target.value)}
          >
            <MenuItem value="nids">Network (NIDS)</MenuItem>
            <MenuItem value="logs">Logs (SIEM)</MenuItem>
            <MenuItem value="phishing">Phishing</MenuItem>
            <MenuItem value="auth">Authentication</MenuItem>
            <MenuItem value="malware">Malware</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Tabs */}
      <Paper>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Trends" />
          <Tab label="Feature Importance" />
          <Tab label="Model Performance" />
          <Tab label="Entity Risk" />
          <Tab label="Attack Patterns" />
        </Tabs>

        {/* Trends Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Alert Volume & Score Trends (Last 30 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="alerts"
                    stroke="#2196f3"
                    strokeWidth={2}
                    name="Alert Count"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="avgScore"
                    stroke="#f50057"
                    strokeWidth={2}
                    name="Avg Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                False Positive Rate
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="falsePositives" fill="#ff9800" name="False Positives" />
                </BarChart>
              </ResponsiveContainer>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Feature Importance Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Top Contributing Features for {selectedDomain.toUpperCase()} Model
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Global feature importance based on SHAP values across all predictions.
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={featureImportance} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 0.3]} />
              <YAxis dataKey="feature" type="category" width={150} />
              <Tooltip />
              <Bar dataKey="importance" fill="#2196f3" name="Importance Score" />
            </BarChart>
          </ResponsiveContainer>
        </TabPanel>

        {/* Model Performance Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Model Performance Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={performanceMetrics}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis domain={[0, 1]} />
                  <Radar
                    name="Performance"
                    dataKey="value"
                    stroke="#2196f3"
                    fill="#2196f3"
                    fillOpacity={0.6}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Metric Breakdown
              </Typography>
              <Box sx={{ mt: 4 }}>
                {performanceMetrics.map((metric) => (
                  <Box key={metric.metric} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{metric.metric}</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {(metric.value * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        width: '100%',
                        height: 8,
                        bgcolor: 'rgba(255,255,255,0.1)',
                        borderRadius: 1,
                      }}
                    >
                      <Box
                        sx={{
                          width: `${metric.value * 100}%`,
                          height: '100%',
                          bgcolor: 'primary.main',
                          borderRadius: 1,
                        }}
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Entity Risk Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            High-Risk Entities
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Entities ranked by cumulative risk score based on recent behavior.
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={entityRiskScores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="entity" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Bar dataKey="risk" fill="#f44336" name="Risk Score" />
            </BarChart>
          </ResponsiveContainer>

          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Risk Summary
            </Typography>
            {entityRiskScores.map((entity) => (
              <Box
                key={entity.entity}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  p: 2,
                  borderBottom: '1px solid rgba(255,255,255,0.1)',
                }}
              >
                <Typography variant="body2">{entity.entity}</Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Typography variant="body2">{(entity.risk * 100).toFixed(0)}%</Typography>
                  <Box
                    sx={{
                      px: 2,
                      py: 0.5,
                      borderRadius: 1,
                      bgcolor:
                        entity.category === 'High'
                          ? '#f443361a'
                          : entity.category === 'Medium'
                          ? '#ff98001a'
                          : '#4caf501a',
                      color:
                        entity.category === 'High'
                          ? '#f44336'
                          : entity.category === 'Medium'
                          ? '#ff9800'
                          : '#4caf50',
                    }}
                  >
                    <Typography variant="caption" fontWeight="bold">
                      {entity.category.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            ))}
          </Box>
        </TabPanel>

        {/* Attack Patterns Tab */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" gutterBottom>
            Detected Attack Patterns (Last 30 Days)
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={anomalyPatterns} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="pattern" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="occurrences" fill="#2196f3" name="Occurrences" />
            </BarChart>
          </ResponsiveContainer>

          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Pattern Analysis
            </Typography>
            {anomalyPatterns.map((pattern) => (
              <Box
                key={pattern.pattern}
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  p: 2,
                  borderBottom: '1px solid rgba(255,255,255,0.1)',
                }}
              >
                <Typography variant="body2">{pattern.pattern}</Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Typography variant="body2">{pattern.occurrences} events</Typography>
                  <Box
                    sx={{
                      px: 2,
                      py: 0.5,
                      borderRadius: 1,
                      bgcolor: pattern.avgSeverity === 'Critical' ? '#f443361a' : '#ff98001a',
                      color: pattern.avgSeverity === 'Critical' ? '#f44336' : '#ff9800',
                    }}
                  >
                    <Typography variant="caption" fontWeight="bold">
                      {pattern.avgSeverity.toUpperCase()}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            ))}
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  )
}
