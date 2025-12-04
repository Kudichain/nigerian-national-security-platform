import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import {
  CheckCircle,
  Warning,
  PlayArrow,
  Stop,
  ExpandMore,
  Security,
  Description,
  School,
  NetworkCheck,
} from '@mui/icons-material'

export default function Pilot() {
  const [activeStep, setActiveStep] = useState(0)

  const pilotPhases = [
    {
      label: 'Airport Selection & Authorization',
      duration: 'Week 0',
      status: 'completed',
      tasks: [
        { text: 'Select pilot airport (MMIA Lagos proposed)', done: true },
        { text: 'Obtain formal authorization from FAAN', done: true },
        { text: 'Sign MOU with airport manager', done: true },
        { text: 'Vendor access credentials issued', done: false },
      ],
      deliverables: ['Signed MOU', 'DSA with airport', 'Access credentials'],
    },
    {
      label: 'Edge Gateway Deployment',
      duration: 'Week 1',
      status: 'in-progress',
      tasks: [
        { text: 'Install edge gateway in secure comms room', done: false },
        { text: 'Connect to 3-5 security cameras', done: false },
        { text: 'Configure drone corridor monitoring', done: false },
        { text: 'Verify TPM attestation', done: false },
        { text: 'Test redundant power & UPS failover', done: false },
      ],
      deliverables: ['Edge hardware operational', 'Network link with QoS', 'UPS backup verified'],
    },
    {
      label: 'Observe-Only Mode',
      duration: 'Weeks 1-4',
      status: 'pending',
      tasks: [
        { text: 'Run AI detection models (no automation)', done: false },
        { text: 'Send alerts to airport security (SMS/email)', done: false },
        { text: 'Collect baseline metrics (false positives)', done: false },
        { text: 'Tune detection thresholds weekly', done: false },
        { text: 'Weekly stakeholder briefings', done: false },
      ],
      deliverables: ['Baseline precision metrics', 'Tuned detection thresholds', 'Operator feedback'],
    },
    {
      label: 'Assisted Mode',
      duration: 'Weeks 5-8',
      status: 'pending',
      tasks: [
        { text: 'Enable human-review case workflows', done: false },
        { text: 'Operator-approved PTZ camera control', done: false },
        { text: 'Track MTTV & MTTA metrics', done: false },
        { text: 'Test dual authorization for critical actions', done: false },
        { text: 'Daily operator training & SOPs review', done: false },
      ],
      deliverables: ['SOPs for case handling', 'Operator training logs', 'HITL approval metrics'],
    },
    {
      label: 'Audit & Sign-Off',
      duration: 'Week 9',
      status: 'pending',
      tasks: [
        { text: 'Third-party privacy audit (NDPR compliance)', done: false },
        { text: 'Security audit (penetration testing)', done: false },
        { text: 'Community stakeholder briefing', done: false },
        { text: 'PIA review & DPO approval', done: false },
        { text: 'Final sign-off from FAAN', done: false },
      ],
      deliverables: ['Audit reports', 'PIA approval', 'Stakeholder sign-off'],
    },
    {
      label: 'Scale to Production',
      duration: 'Week 10+',
      status: 'pending',
      tasks: [
        { text: 'Expand to additional camera groups', done: false },
        { text: 'Deploy to second airport (Abuja FCT)', done: false },
        { text: 'Integrate with national threat database', done: false },
        { text: 'Enable automated response (with safeguards)', done: false },
      ],
      deliverables: ['Multi-airport deployment', 'National integration', 'Production SLA'],
    },
  ]

  const preflightChecklist = [
    { item: 'Signed MOU & DSA with airport', status: 'done', icon: <Description /> },
    { item: 'Vendor access credentials', status: 'pending', icon: <Security /> },
    { item: 'PIA completed and approved by DPO', status: 'done', icon: <CheckCircle /> },
    { item: 'Edge hardware with TPM attestation', status: 'done', icon: <NetworkCheck /> },
    { item: 'Redundant power & UPS (4-hour backup)', status: 'pending', icon: <Warning /> },
    { item: 'Private APN/VPN with QoS guarantees', status: 'done', icon: <NetworkCheck /> },
    { item: 'Operator training & SOPs documented', status: 'in-progress', icon: <School /> },
  ]

  const kpiMetrics = [
    {
      category: 'Stream Health',
      metrics: [
        { name: 'Packet Loss', value: '0.02%', target: '<0.1%', status: 'good' },
        { name: 'Network Latency', value: '12ms', target: '<50ms', status: 'good' },
        { name: 'Camera Uptime', value: '99.8%', target: '>99.5%', status: 'good' },
        { name: 'Drone Link Quality', value: '95%', target: '>90%', status: 'good' },
      ],
    },
    {
      category: 'AI Performance',
      metrics: [
        { name: 'Precision @ Top-K', value: '94.2%', target: '>90%', status: 'good' },
        { name: 'False Positive Rate', value: '5.8%', target: '<10%', status: 'good' },
        { name: 'Detection Latency', value: '180ms', target: '<500ms', status: 'good' },
        { name: 'Model Drift (weekly)', value: '0.3%', target: '<2%', status: 'good' },
      ],
    },
    {
      category: 'Operator Workload',
      metrics: [
        { name: 'Alerts per Operator/Hour', value: '12', target: '<15', status: 'good' },
        { name: 'Mean Time to Verify (MTTV)', value: '45s', target: '<60s', status: 'good' },
        { name: 'Mean Time to Action (MTTA)', value: '3.2min', target: '<5min', status: 'good' },
        { name: 'Case Backlog', value: '3', target: '<10', status: 'good' },
      ],
    },
    {
      category: 'Security & Audit',
      metrics: [
        { name: 'Audit Access Frequency', value: '8/day', target: 'Monitor', status: 'neutral' },
        { name: 'Suspicious Access Attempts', value: '0', target: '0', status: 'good' },
        { name: 'Failed Auth Attempts', value: '2', target: '<5/day', status: 'good' },
        { name: 'Audit Log Integrity', value: '100%', target: '100%', status: 'good' },
      ],
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Airport Pilot Program
      </Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight="bold">
          90-Day Regulatory Sandbox Pilot - MMIA Lagos
        </Typography>
        <Typography variant="body2">
          Privacy-first deployment with observe-only → assisted mode progression. FAAN authorization secured.
        </Typography>
      </Alert>

      {/* Preflight Checklist */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Pre-Flight Checklist
        </Typography>
        <Grid container spacing={2}>
          {preflightChecklist.map((item, idx) => (
            <Grid item xs={12} md={6} key={idx}>
              <Card
                sx={{
                  borderLeft: `4px solid ${
                    item.status === 'done' ? '#4caf50' : item.status === 'pending' ? '#ff9800' : '#2196f3'
                  }`,
                }}
              >
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box
                    sx={{
                      color: item.status === 'done' ? '#4caf50' : item.status === 'pending' ? '#ff9800' : '#2196f3',
                    }}
                  >
                    {item.icon}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2">{item.item}</Typography>
                  </Box>
                  <Chip
                    label={item.status.toUpperCase()}
                    size="small"
                    color={item.status === 'done' ? 'success' : item.status === 'pending' ? 'warning' : 'info'}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Pilot Phases */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Pilot Deployment Phases
        </Typography>
        <Stepper activeStep={activeStep} orientation="vertical">
          {pilotPhases.map((phase, index) => (
            <Step key={index} expanded>
              <StepLabel
                optional={
                  <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                    <Chip label={phase.duration} size="small" variant="outlined" />
                    <Chip
                      label={phase.status.toUpperCase()}
                      size="small"
                      color={
                        phase.status === 'completed'
                          ? 'success'
                          : phase.status === 'in-progress'
                          ? 'info'
                          : 'default'
                      }
                    />
                  </Box>
                }
              >
                <Typography variant="subtitle1" fontWeight="bold">
                  {phase.label}
                </Typography>
              </StepLabel>
              <StepContent>
                <List dense>
                  {phase.tasks.map((task, idx) => (
                    <ListItem key={idx}>
                      <ListItemIcon>
                        {task.done ? <CheckCircle color="success" /> : <Warning color="warning" />}
                      </ListItemIcon>
                      <ListItemText
                        primary={task.text}
                        sx={{ textDecoration: task.done ? 'line-through' : 'none' }}
                      />
                    </ListItem>
                  ))}
                </List>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight="bold">
                    Deliverables:
                  </Typography>
                  <Typography variant="body2">{phase.deliverables.join(' • ')}</Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => setActiveStep(index + 1)}
                    disabled={index === pilotPhases.length - 1}
                  >
                    {index === pilotPhases.length - 1 ? 'Completed' : 'Continue to Next Phase'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* KPI Dashboard */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Live Monitoring & KPIs
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Real-time operational metrics for dashboard operators
        </Typography>

        {kpiMetrics.map((category, idx) => (
          <Accordion key={idx} defaultExpanded={idx === 0}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1" fontWeight="bold">
                {category.category}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Metric</TableCell>
                      <TableCell align="right">Current Value</TableCell>
                      <TableCell align="right">Target</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {category.metrics.map((metric, midx) => (
                      <TableRow key={midx}>
                        <TableCell>{metric.name}</TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold">
                            {metric.value}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="text.secondary">
                            {metric.target}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={metric.status === 'good' ? 'ON TARGET' : 'MONITOR'}
                            size="small"
                            color={metric.status === 'good' ? 'success' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>

      {/* Operational Controls */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Pilot Controls
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              color="success"
              fullWidth
              startIcon={<PlayArrow />}
              disabled={activeStep !== 1}
            >
              Start Observe Mode
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button variant="contained" color="info" fullWidth startIcon={<Security />} disabled={activeStep < 3}>
              Enable Assisted Mode
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button variant="outlined" color="warning" fullWidth startIcon={<Stop />}>
              Emergency Stop
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button variant="outlined" fullWidth startIcon={<Description />}>
              Export Audit Report
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}
