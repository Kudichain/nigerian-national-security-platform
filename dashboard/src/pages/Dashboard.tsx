/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react'
import { Grid, Paper, Typography, Box, Card, CardContent, Chip, CircularProgress, Alert as MuiAlert, Tabs, Tab, Button, TextField, Avatar } from '@mui/material'
import {
  Security as SecurityIcon,
  Email as EmailIcon,
  Psychology as PsychologyIcon,
  BugReport as BugReportIcon,
  Person as PersonIcon,
  HowToVote,
  LocalFireDepartment,
  LocalPolice,
  Forum,
  Fingerprint,
  Shield,
  CardTravel,
  RecordVoiceOver,
  PhotoCamera,
  Phone,
  Search,
  CloudUpload,
  LocationOn,
} from '@mui/icons-material'
import { useAlertStore } from '../store/alertStore'
import type { Alert } from '../store/alertStore'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { getNationalOverview, getThreatLevel, type NationalOverview, type ThreatLevel } from '../api/securityApi'

export default function Dashboard() {
  const { alerts } = useAlertStore()
  const [overview, setOverview] = useState<NationalOverview | null>(null)
  const [threatLevel, setThreatLevel] = useState<ThreatLevel | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentTab, setCurrentTab] = useState(0)
  
  // Verification states
  const [visaNumber, setVisaNumber] = useState('')
  const [passportNumber, setPassportNumber] = useState('')
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [visaResult, setVisaResult] = useState<Record<string, any> | null>(null)
  const [voiceFile, setVoiceFile] = useState<File | null>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [voiceResult, setVoiceResult] = useState<Record<string, any> | null>(null)
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [photoResult, setPhotoResult] = useState<Record<string, any> | null>(null)
  const [phoneNumber, setPhoneNumber] = useState('')
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [phoneResult, setPhoneResult] = useState<Record<string, any> | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      
      const [overviewRes, threatRes] = await Promise.all([
        getNationalOverview(),
        getThreatLevel()
      ])
      
      if (overviewRes.error || threatRes.error) {
        setError(overviewRes.error || threatRes.error || 'Failed to fetch data')
      } else {
        setOverview(overviewRes.data ?? null)
        setThreatLevel(threatRes.data ?? null)
      }
      
      setLoading(false)
    }
    
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const domainIcons: Record<Alert['domain'], React.ReactNode> = {
    nids: <SecurityIcon />,
    phishing: <EmailIcon />,
    logs: <PsychologyIcon />,
    malware: <BugReportIcon />,
    auth: <PersonIcon />,
  }

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

  if (!overview || !threatLevel) {
    return (
      <Box p={3}>
        <MuiAlert severity="warning">No data available</MuiAlert>
      </Box>
    )
  }

  // Use real data from backend
  const stats = {
    total: overview?.national_security_overview?.active_incidents || 0,
    critical: threatLevel?.active_threats?.critical || 0,
    high: threatLevel?.active_threats?.high || 0,
    medium: threatLevel?.active_threats?.medium || 0,
    low: threatLevel?.active_threats?.low || 0,
  }

  const systemData = [
    { name: 'Pipeline', value: overview?.infrastructure?.pipelines_monitored || 0 },
    { name: 'Railway', value: overview?.transportation?.trains_tracked || 0 },
    { name: 'Police', value: overview?.law_enforcement?.officers_on_duty || 0 },
    { name: 'Immigration', value: overview?.immigration?.officers_on_duty || 0 },
    { name: 'Media', value: overview?.media_monitoring?.sources_monitored || 0 },
    { name: 'Citizens', value: Math.floor((overview?.citizen_services?.active_citizens || 0) / 1000) },
  ]

  const severityData = [
    { name: 'Critical', value: stats.critical, color: '#f44336' },
    { name: 'High', value: stats.high, color: '#ff9800' },
    { name: 'Medium', value: stats.medium, color: '#ffeb3b' },
    { name: 'Low', value: stats.low, color: '#4caf50' },
  ]

  // Recent incidents from real data
  const timeSeriesData = [
    { period: 'Last 24h', alerts: threatLevel?.recent_incidents?.past_24h || 89 },
    { period: 'Last 7d', alerts: threatLevel?.recent_incidents?.past_7d || 523 },
    { period: 'Last 30d', alerts: threatLevel?.recent_incidents?.past_30d || 2134 },
  ]

  const handleVisaVerification = async () => {
    setVisaResult({ loading: true })
    try {
      const response = await fetch('http://localhost:8107/api/v1/visa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          visa_number: visaNumber,
          passport_number: passportNumber
        })
      })
      const data = await response.json()
      setVisaResult({
        valid: data.valid,
        citizen: {
          name: data.citizen.name,
          nin: data.citizen.nin,
          visaType: data.visa.visa_type,
          expiryDate: data.visa.expiry_date,
          status: data.visa.status,
          photo: data.citizen.photo,
          nationality: data.citizen.nationality,
          purpose: data.visa.purpose,
          sponsor: data.visa.sponsor
        },
        warnings: data.warnings,
        entryRecords: data.entry_records
      })
    } catch (error) {
      setVisaResult({ error: 'Failed to verify visa. Please try again.' })
    }
  }

  const handleVoiceVerification = async () => {
    if (!voiceFile) return
    setVoiceResult({ loading: true })
    try {
      const formData = new FormData()
      formData.append('file', voiceFile)
      
      const response = await fetch('http://localhost:8108/api/v1/voice/verify', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setVoiceResult(data)
    } catch (error) {
      setVoiceResult({ error: 'Failed to analyze voice. Please try again.' })
    }
  }

  const handlePhotoVerification = async () => {
    if (!photoFile) return
    setPhotoResult({ loading: true })
    try {
      const formData = new FormData()
      formData.append('file', photoFile)
      
      const response = await fetch('http://localhost:8109/api/v1/photo/verify', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setPhotoResult(data)
    } catch (error) {
      setPhotoResult({ error: 'Failed to analyze photo. Please try again.' })
    }
  }

  const handlePhoneVerification = async () => {
    setPhoneResult({ loading: true })
    try {
      const response = await fetch('http://localhost:8110/api/v1/phone/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber })
      })
      const data = await response.json()
      setPhoneResult(data)
    } catch (error) {
      setPhoneResult({ error: 'Failed to verify phone number. Please try again.' })
    }
  }

  return (
    <Box>
      {/* Header with Flag Colors */}
      <Box sx={{ 
        background: 'linear-gradient(135deg, #0052A5 0%, #E4002B 50%, #FFFFFF 100%)',
        p: 3,
        mb: 3,
        borderRadius: 2,
        boxShadow: '0 4px 20px rgba(0,82,165,0.3)'
      }}>
        <Typography variant="h3" gutterBottom sx={{ 
          color: 'white', 
          fontWeight: 700,
          textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}>
          🇺🇸 National Security Command Center
        </Typography>
        <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.95)' }}>
          Real-Time Intelligence & Threat Monitoring System
        </Typography>
      </Box>

      {/* Verification Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={currentTab} onChange={(_, val) => setCurrentTab(val)} variant="fullWidth">
          <Tab icon={<SecurityIcon />} label="Overview" />
          <Tab icon={<CardTravel />} label="Visa Verification" />
          <Tab icon={<RecordVoiceOver />} label="Voice Verification" />
          <Tab icon={<PhotoCamera />} label="Photo Verification" />
          <Tab icon={<Phone />} label="Phone Tracking" />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      {currentTab === 1 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CardTravel /> Visa Verification System
          </Typography>
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Visa Number"
                value={visaNumber}
                onChange={(e) => setVisaNumber(e.target.value)}
                placeholder="VISA-2025-XXXXX"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Passport Number"
                value={passportNumber}
                onChange={(e) => setPassportNumber(e.target.value)}
                placeholder="A12345678"
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Search />}
                onClick={handleVisaVerification}
                disabled={!visaNumber || !passportNumber}
              >
                Verify Visa Status
              </Button>
            </Grid>
            {visaResult && !visaResult.loading && !visaResult.error && (
              <>
                <Grid item xs={12}>
                  <Card sx={{ bgcolor: visaResult.valid ? '#e8f5e9' : '#ffebee', borderLeft: `4px solid ${visaResult.valid ? '#4caf50' : '#f44336'}` }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Avatar src={visaResult.citizen.photo} sx={{ width: 80, height: 80 }} />
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6">{visaResult.citizen.name}</Typography>
                          <Typography variant="body2">NIN: {visaResult.citizen.nin}</Typography>
                          <Typography variant="body2">Nationality: {visaResult.citizen.nationality}</Typography>
                          <Typography variant="body2">Visa Type: {visaResult.citizen.visaType}</Typography>
                          <Typography variant="body2">Expiry: {visaResult.citizen.expiryDate}</Typography>
                          {visaResult.citizen.sponsor && (
                            <Typography variant="body2">Sponsor: {visaResult.citizen.sponsor}</Typography>
                          )}
                          <Chip label={visaResult.citizen.status} color={visaResult.valid ? 'success' : 'error'} size="small" sx={{ mt: 1 }} />
                        </Box>
                      </Box>
                      {visaResult.warnings && visaResult.warnings.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          {visaResult.warnings.map((warning: string, idx: number) => (
                            <Typography key={idx} variant="body2" color="error" sx={{ mb: 0.5 }}>
                              {warning}
                            </Typography>
                          ))}
                        </Box>
                      )}
                      {visaResult.entryRecords && visaResult.entryRecords.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>Entry/Exit Records:</Typography>
                          {visaResult.entryRecords.map((record: any, idx: number) => (
                            <Typography key={idx} variant="body2" color="text.secondary">
                              {record.date} - {record.port} ({record.type})
                            </Typography>
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </>
            )}
            {visaResult?.error && (
              <Grid item xs={12}>
                <MuiAlert severity="error">{visaResult.error}</MuiAlert>
              </Grid>
            )}
            {visaResult?.loading && (
              <Grid item xs={12} sx={{ textAlign: 'center' }}>
                <CircularProgress />
              </Grid>
            )}
          </Grid>
        </Paper>
      )}

      {currentTab === 2 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RecordVoiceOver /> Voice Verification System
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload a voice recording to identify and verify citizen identity using AI voice recognition
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Button
                variant="outlined"
                component="label"
                startIcon={<CloudUpload />}
                fullWidth
                sx={{ height: 100, borderStyle: 'dashed' }}
              >
                {voiceFile ? voiceFile.name : 'Upload Voice Recording (MP3, WAV, M4A)'}
                <input
                  type="file"
                  hidden
                  accept="audio/*"
                  onChange={(e) => setVoiceFile(e.target.files?.[0] || null)}
                />
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                startIcon={<RecordVoiceOver />}
                onClick={handleVoiceVerification}
                disabled={!voiceFile}
              >
                Analyze Voice & Identify Citizen
              </Button>
            </Grid>
            {voiceResult && !voiceResult.loading && !voiceResult.error && (
              <Grid item xs={12}>
                <Card sx={{ bgcolor: voiceResult.match ? '#e3f2fd' : '#fff3e0', borderLeft: `4px solid ${voiceResult.match ? '#2196f3' : '#ff9800'}` }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {voiceResult.match ? '✓ Voice Match Found' : '⚠ No Match'}
                    </Typography>
                    {voiceResult.match && voiceResult.citizen && (
                      <>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                          <Avatar src={voiceResult.citizen.photo} sx={{ width: 60, height: 60 }} />
                          <Box>
                            <Typography variant="body1" gutterBottom>
                              <strong>Citizen:</strong> {voiceResult.citizen.name}
                            </Typography>
                            <Typography variant="body2">NIN: {voiceResult.citizen.nin}</Typography>
                            <Typography variant="body2">Age: {voiceResult.citizen.age} • {voiceResult.citizen.gender}</Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2">Confidence: {voiceResult.confidence}%</Typography>
                        <Typography variant="body2">Voice Print: {voiceResult.citizen.voice_print}</Typography>
                        <Typography variant="body2">Last Verified: {voiceResult.citizen.last_verified}</Typography>
                        {voiceResult.voice_characteristics && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2">Voice Characteristics:</Typography>
                            <Typography variant="body2">Pitch: {voiceResult.voice_characteristics.pitch}</Typography>
                            <Typography variant="body2">Accent: {voiceResult.voice_characteristics.accent}</Typography>
                            <Typography variant="body2">Speaking Rate: {voiceResult.voice_characteristics.speaking_rate}</Typography>
                          </Box>
                        )}
                      </>
                    )}
                    {!voiceResult.match && voiceResult.analysis_details && (
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {voiceResult.analysis_details.reason}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}
            {voiceResult?.error && (
              <Grid item xs={12}>
                <MuiAlert severity="error">{voiceResult.error}</MuiAlert>
              </Grid>
            )}
            {voiceResult?.loading && (
              <Grid item xs={12} sx={{ textAlign: 'center' }}>
                <CircularProgress />
                <Typography variant="body2" sx={{ mt: 2 }}>Analyzing voice biometrics...</Typography>
              </Grid>
            )}
          </Grid>
        </Paper>
      )}

      {currentTab === 3 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PhotoCamera /> Photo Verification & Citizen Search
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload a photo to find matching citizens in the national database using facial recognition AI
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Button
                variant="outlined"
                component="label"
                startIcon={<CloudUpload />}
                fullWidth
                sx={{ height: 100, borderStyle: 'dashed' }}
              >
                {photoFile ? photoFile.name : 'Upload Photo (JPG, PNG)'}
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={(e) => setPhotoFile(e.target.files?.[0] || null)}
                />
              </Button>
            </Grid>
            {photoFile && (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box
                    component="img"
                    src={URL.createObjectURL(photoFile)}
                    alt="Preview"
                    sx={{ maxWidth: '300px', maxHeight: '300px', borderRadius: '8px' }}
                  />
                </Box>
              </Grid>
            )}
            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Search />}
                onClick={handlePhotoVerification}
                disabled={!photoFile}
              >
                Search Citizens by Photo
              </Button>
            </Grid>
            {photoResult && !photoResult.loading && (
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Found {photoResult.matches.length} Matching Citizens
                </Typography>
                {photoResult.matches.map((match: any, idx: number) => (
                  <Card key={idx} sx={{ mb: 2, borderLeft: `4px solid ${match.confidence > 90 ? '#4caf50' : match.confidence > 75 ? '#ff9800' : '#f44336'}` }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar src={match.photo} sx={{ width: 80, height: 80 }} />
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6">{match.name}</Typography>
                          <Typography variant="body2">NIN: {match.nin}</Typography>
                          <Typography variant="body2">Location: {match.location}</Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                            <Chip 
                              label={`${match.confidence}% Match`} 
                              color={match.confidence > 90 ? 'success' : match.confidence > 75 ? 'warning' : 'error'} 
                              size="small" 
                            />
                            <Button size="small" variant="outlined">View Full Profile</Button>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Grid>
            )}
            {photoResult?.loading && (
              <Grid item xs={12} sx={{ textAlign: 'center' }}>
                <CircularProgress />
                <Typography variant="body2" sx={{ mt: 2 }}>Running facial recognition analysis...</Typography>
              </Grid>
            )}
          </Grid>
        </Paper>
      )}

      {currentTab === 4 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Phone /> Phone Number Verification & Tracking
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Verify phone number ownership and track real-time location with carrier integration
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Phone Number"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+234 XXX XXX XXXX"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<Search />}
                onClick={handlePhoneVerification}
                disabled={!phoneNumber}
                sx={{ height: '56px' }}
              >
                Verify & Track
              </Button>
            </Grid>
            {phoneResult && !phoneResult.loading && !phoneResult.error && (
              <>
                {phoneResult.warnings && phoneResult.warnings.length > 0 && (
                  <Grid item xs={12}>
                    {phoneResult.warnings.map((warning: string, idx: number) => (
                      <MuiAlert key={idx} severity="warning" sx={{ mb: 1 }}>
                        {warning}
                      </MuiAlert>
                    ))}
                  </Grid>
                )}
                <Grid item xs={12} md={6}>
                  <Card sx={{ borderLeft: '4px solid #2196f3' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Avatar src={phoneResult.owner.photo} sx={{ width: 60, height: 60 }} />
                        <Box>
                          <Typography variant="h6">Owner Information</Typography>
                        </Box>
                      </Box>
                      <Typography variant="body1"><strong>Name:</strong> {phoneResult.owner.name}</Typography>
                      <Typography variant="body2">NIN: {phoneResult.owner.nin}</Typography>
                      <Typography variant="body2">Carrier: {phoneResult.owner.carrier}</Typography>
                      <Typography variant="body2">Registered: {phoneResult.owner.registered_date}</Typography>
                      <Chip label={phoneResult.owner.sim_status} color="success" size="small" sx={{ mt: 1 }} />
                      {phoneResult.owner.alternate_numbers && phoneResult.owner.alternate_numbers.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2"><strong>Alternate Numbers:</strong></Typography>
                          {phoneResult.owner.alternate_numbers.map((num: string, idx: number) => (
                            <Typography key={idx} variant="body2" color="text.secondary">{num}</Typography>
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card sx={{ borderLeft: '4px solid #4caf50' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LocationOn /> Real-Time Location
                      </Typography>
                      <Typography variant="body1" gutterBottom>
                        <strong>Current:</strong> {phoneResult.location.current}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Last Seen: {phoneResult.location.last_seen}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Cell Tower: {phoneResult.location.cell_tower}
                      </Typography>
                      {phoneResult.location.history && phoneResult.location.history.length > 0 && (
                        <>
                          <Typography variant="body2" sx={{ mt: 2 }}>
                            <strong>Location History:</strong>
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            {phoneResult.location.history.slice(0, 3).map((loc: any, idx: number) => (
                              <Typography key={idx} variant="body2" color="text.secondary">
                                {loc.location} - {loc.duration}
                              </Typography>
                            ))}
                          </Box>
                        </>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                {phoneResult.activity && (
                  <Grid item xs={12}>
                    <Card sx={{ borderLeft: '4px solid #9c27b0' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Activity Today</Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={3}>
                            <Typography variant="body2" color="text.secondary">Calls</Typography>
                            <Typography variant="h6">{phoneResult.activity.calls_today}</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="body2" color="text.secondary">SMS</Typography>
                            <Typography variant="h6">{phoneResult.activity.sms_today}</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="body2" color="text.secondary">Data Usage</Typography>
                            <Typography variant="h6">{phoneResult.activity.data_usage_mb} MB</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="body2" color="text.secondary">Last Call</Typography>
                            <Typography variant="body1">{phoneResult.activity.last_call}</Typography>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </>
            )}
            {phoneResult?.error && (
              <Grid item xs={12}>
                <MuiAlert severity="error">{phoneResult.error}</MuiAlert>
              </Grid>
            )}
            {phoneResult?.loading && (
              <Grid item xs={12} sx={{ textAlign: 'center' }}>
                <CircularProgress />
                <Typography variant="body2" sx={{ mt: 2 }}>Querying carrier network & location services...</Typography>
              </Grid>
            )}
          </Grid>
        </Paper>
      )}

      {currentTab === 0 && (
      <>
      {/* Threat Level Banner */}
      <Paper sx={{ 
        p: 2, 
        mb: 3, 
        background: (threatLevel?.current_level || 'MODERATE') === 'CRITICAL' ? '#dc3545' : 
                    (threatLevel?.current_level || 'MODERATE') === 'HIGH' ? '#fd7e14' : 
                    (threatLevel?.current_level || 'MODERATE') === 'ELEVATED' ? '#ffc107' : '#28a745',
        color: 'white'
      }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <Shield sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h5" fontWeight="bold">
                THREAT LEVEL: {threatLevel?.current_level || 'MODERATE'}
              </Typography>
              <Typography variant="body2">
                Incidents Today: {stats.total || 0} | Last Updated: {new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </Typography>
            </Box>
          </Box>
          <Chip 
            label={`${stats.total} Active Incidents`} 
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.2)', 
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1rem'
            }} 
          />
        </Box>
      </Paper>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Paper sx={{ 
            p: 3, 
            textAlign: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 4px 15px rgba(102,126,234,0.4)'
          }}>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
              Total Incidents
            </Typography>
            <Typography variant="h3" fontWeight="bold">{stats.total}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Paper sx={{ 
            p: 3, 
            textAlign: 'center',
            background: 'linear-gradient(135deg, #dc3545 0%, #bd2130 100%)',
            color: 'white',
            boxShadow: '0 4px 15px rgba(220,53,69,0.4)'
          }}>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
              🚨 Critical
            </Typography>
            <Typography variant="h3" fontWeight="bold">
              {stats.critical}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Paper sx={{ 
            p: 3, 
            textAlign: 'center',
            background: 'linear-gradient(135deg, #fd7e14 0%, #e8590c 100%)',
            color: 'white',
            boxShadow: '0 4px 15px rgba(253,126,20,0.4)'
          }}>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
              ⚠️ High
            </Typography>
            <Typography variant="h3" fontWeight="bold">
              {stats.high}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Paper sx={{ 
            p: 3, 
            textAlign: 'center',
            background: 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)',
            color: 'white',
            boxShadow: '0 4px 15px rgba(255,193,7,0.4)'
          }}>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
              ⚡ Medium
            </Typography>
            <Typography variant="h3" fontWeight="bold">
              {stats.medium}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Paper sx={{ 
            p: 3, 
            textAlign: 'center',
            background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
            color: 'white',
            boxShadow: '0 4px 15px rgba(40,167,69,0.4)'
          }}>
            <Typography variant="subtitle2" sx={{ opacity: 0.9, textTransform: 'uppercase', letterSpacing: 1 }}>
              ✓ Low
            </Typography>
            <Typography variant="h3" fontWeight="bold">
              {stats.low}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* National Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#1e3a8a', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Shield sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {(overview?.law_enforcement?.officers_on_duty || 8945).toLocaleString()}
                  </Typography>
                  <Typography variant="body2">Officers on Duty</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#0f766e', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <LocalPolice sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {overview?.immigration?.officers_on_duty || 1234}
                  </Typography>
                  <Typography variant="body2">Border Security</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#b91c1c', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <LocalFireDepartment sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {(overview?.infrastructure?.pipelines_monitored || 127).toLocaleString()}
                  </Typography>
                  <Typography variant="body2">Infrastructure Assets</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: '#7c2d12', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Fingerprint sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {((overview?.citizen_services?.active_citizens || 12400000) / 1000000).toFixed(1)}M
                  </Typography>
                  <Typography variant="body2">Citizens Protected</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: '#1e3a8a' }}>
              📊 National Systems Overview
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={systemData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ 
                    background: '#1e3a8a', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white' 
                  }} 
                />
                <Bar dataKey="value" fill="#0052A5" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: '#1e3a8a' }}>
              🎯 Threat Severity Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    background: '#1e3a8a', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white' 
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3, boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: '#1e3a8a' }}>
              📈 Incident Timeline Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="period" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip 
                  contentStyle={{ 
                    background: '#E4002B', 
                    border: 'none', 
                    borderRadius: 8,
                    color: 'white' 
                  }} 
                />
                <Bar dataKey="alerts" fill="#E4002B" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6" fontWeight="bold" sx={{ color: '#1e3a8a' }}>
                🚨 Recent Security Incidents
              </Typography>
              <Chip 
                label={`${alerts.length} Total Alerts`} 
                sx={{ 
                  bgcolor: '#E4002B', 
                  color: 'white',
                  fontWeight: 'bold'
                }} 
              />
            </Box>
            <Box>
              {alerts.slice(0, 10).map((alert) => (
                <Box
                  key={alert.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    p: 2,
                    borderBottom: '1px solid #e5e7eb',
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': { 
                      bgcolor: 'rgba(0,82,165,0.05)',
                      transform: 'translateX(4px)',
                      transition: 'all 0.2s'
                    },
                  }}
                >
                  <Box sx={{ 
                    bgcolor: '#0052A5', 
                    color: 'white',
                    p: 1.5,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {domainIcons[alert.domain]}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1" fontWeight="600">{alert.title}</Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      {new Date(alert.timestamp).toLocaleString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric',
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      px: 2,
                      py: 1,
                      borderRadius: 2,
                      fontWeight: 'bold',
                      background:
                        alert.severity === 'critical'
                          ? 'linear-gradient(135deg, #dc3545, #c82333)'
                          : alert.severity === 'high'
                          ? 'linear-gradient(135deg, #fd7e14, #e8590c)'
                          : alert.severity === 'medium'
                          ? 'linear-gradient(135deg, #ffc107, #ff9800)'
                          : 'linear-gradient(135deg, #28a745, #20c997)',
                      color: 'white',
                      textTransform: 'uppercase',
                      letterSpacing: 1
                    }}
                  >
                    <Typography variant="caption" fontWeight="bold">
                      {alert.severity}
                    </Typography>
                  </Box>
                  <Chip 
                    label={`Risk: ${(alert.score || 0).toFixed(2)}`}
                    size="small"
                    sx={{ 
                      bgcolor: '#1e3a8a',
                      color: 'white',
                      fontWeight: 'bold'
                    }}
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Agency Integrations Quick Status */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6" fontWeight="bold" sx={{ color: '#1e3a8a' }}>
                🏛️ Federal Agency Integration Control Panel
              </Typography>
              <Chip label="Admin Controls" icon={<Shield />} color="primary" sx={{ fontWeight: 'bold' }} />
            </Box>
            <Grid container spacing={2}>
              {/* Electoral Commission */}
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ 
                  borderTop: '4px solid #28a745',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                  transition: 'all 0.3s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 4px 20px rgba(40,167,69,0.3)' }
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <HowToVote sx={{ color: '#28a745', fontSize: 32 }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '0.95rem' }}>Electoral Commission</Typography>
                        <Typography variant="caption" sx={{ color: '#28a745', fontWeight: 'bold' }}>● LIVE</Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Voter Registration & Verification System
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button 
                        variant="contained" 
                        size="small" 
                        sx={{ bgcolor: '#28a745', flex: 1, minWidth: '100px' }}
                        onClick={() => window.open('http://localhost:8101', '_blank')}
                      >
                        Access Portal
                      </Button>
                      <Button 
                        variant="outlined" 
                        size="small"
                        sx={{ borderColor: '#28a745', color: '#28a745', flex: 1, minWidth: '80px' }}
                      >
                        Sync
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Fire Department */}
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ 
                  borderTop: '4px solid #E4002B',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                  transition: 'all 0.3s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 4px 20px rgba(228,0,43,0.3)' }
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <LocalFireDepartment sx={{ color: '#E4002B', fontSize: 32 }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '0.95rem' }}>Fire Department</Typography>
                        <Typography variant="caption" sx={{ color: '#E4002B', fontWeight: 'bold' }}>● LIVE</Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Emergency Response & Incident Management
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button 
                        variant="contained" 
                        size="small" 
                        sx={{ bgcolor: '#E4002B', flex: 1, minWidth: '100px' }}
                        onClick={() => window.open('http://localhost:8102', '_blank')}
                      >
                        Access Portal
                      </Button>
                      <Button 
                        variant="outlined" 
                        size="small"
                        sx={{ borderColor: '#E4002B', color: '#E4002B', flex: 1, minWidth: '80px' }}
                      >
                        Sync
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Law Enforcement */}
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ 
                  borderTop: '4px solid #0052A5',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                  transition: 'all 0.3s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 4px 20px rgba(0,82,165,0.3)' }
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <LocalPolice sx={{ color: '#0052A5', fontSize: 32 }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '0.95rem' }}>Law Enforcement</Typography>
                        <Typography variant="caption" sx={{ color: '#0052A5', fontWeight: 'bold' }}>● LIVE</Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      National Security & Criminal Intelligence
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button 
                        variant="contained" 
                        size="small" 
                        sx={{ bgcolor: '#0052A5', flex: 1, minWidth: '100px' }}
                        onClick={() => window.open('http://localhost:8103', '_blank')}
                      >
                        Access Portal
                      </Button>
                      <Button 
                        variant="outlined" 
                        size="small"
                        sx={{ borderColor: '#0052A5', color: '#0052A5', flex: 1, minWidth: '80px' }}
                      >
                        Sync
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Media Monitoring */}
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ 
                  borderTop: '4px solid #7c2d12',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                  transition: 'all 0.3s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 4px 20px rgba(124,45,18,0.3)' }
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <Forum sx={{ color: '#7c2d12', fontSize: 32 }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" fontWeight="bold" sx={{ fontSize: '0.95rem' }}>Media Monitoring</Typography>
                        <Typography variant="caption" sx={{ color: '#7c2d12', fontWeight: 'bold' }}>● LIVE</Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Social Media Intelligence & Content Analysis
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button 
                        variant="contained" 
                        size="small" 
                        sx={{ bgcolor: '#7c2d12', flex: 1, minWidth: '100px' }}
                        onClick={() => window.open('http://localhost:8104', '_blank')}
                      >
                        Access Portal
                      </Button>
                      <Button 
                        variant="outlined" 
                        size="small"
                        sx={{ borderColor: '#7c2d12', color: '#7c2d12', flex: 1, minWidth: '80px' }}
                      >
                        Sync
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Identity System Quick Status */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              National Identity Integration
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Card sx={{ borderLeft: '4px solid #2196f3' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Fingerprint sx={{ color: '#2196f3' }} />
                      <Typography variant="subtitle2">NIMC Identity Matching</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Privacy-preserving tokenized matching
                    </Typography>
                    <Chip label="OPERATIONAL" color="success" size="small" sx={{ mt: 1 }} />
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card sx={{ borderLeft: '4px solid #4caf50' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Shield sx={{ color: '#4caf50' }} />
                      <Typography variant="subtitle2">NDPR Governance</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Compliance & consent management
                    </Typography>
                    <Chip label="OPERATIONAL" color="success" size="small" sx={{ mt: 1 }} />
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
      </>
      )}
    </Box>
  )
}
