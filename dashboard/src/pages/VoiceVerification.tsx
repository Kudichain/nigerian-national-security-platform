import { useState } from 'react'
import { Box, Paper, Typography, Button, Grid, Card, CardContent, Avatar, Chip, CircularProgress, Alert } from '@mui/material'
import { RecordVoiceOver, CloudUpload, CheckCircle, Error } from '@mui/icons-material'

export default function VoiceVerification() {
  const [voiceFile, setVoiceFile] = useState<File | null>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<Record<string, any> | null>(null)
  const [loading, setLoading] = useState(false)

  const handleVerify = async () => {
    if (!voiceFile) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', voiceFile)
      
      const response = await fetch('http://localhost:8000/api/v1/voice/verify', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ error: 'Failed to analyze voice. Please ensure service is running.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <RecordVoiceOver sx={{ fontSize: 40 }} /> Voice Verification System
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        AI-powered voice biometric identification using advanced audio analysis
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUpload />}
              fullWidth
              sx={{ height: 120, borderStyle: 'dashed', borderWidth: 2 }}
            >
              {voiceFile ? voiceFile.name : 'Upload Voice Sample (MP3, WAV, M4A)'}
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
              fullWidth
              onClick={handleVerify}
              disabled={!voiceFile || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <RecordVoiceOver />}
            >
              {loading ? 'Analyzing Voice...' : 'Verify Voice'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {result && !loading && (
        <Paper sx={{ p: 3 }}>
          {result.error ? (
            <Alert severity="error">{result.error}</Alert>
          ) : result.match ? (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <CheckCircle sx={{ fontSize: 48, color: 'success.main' }} />
                <Box>
                  <Typography variant="h5" color="success.main">Voice Match Found</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Confidence: {result.confidence}%
                  </Typography>
                </Box>
              </Box>

              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Avatar src={result.citizen.photo} sx={{ width: 80, height: 80 }} />
                    <Box>
                      <Typography variant="h6">{result.citizen.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        NIN: {result.citizen.nin}
                      </Typography>
                    </Box>
                  </Box>

                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>Voice Characteristics:</Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Chip label={`Pitch: ${result.voice_characteristics.pitch}`} size="small" />
                    </Grid>
                    <Grid item xs={6}>
                      <Chip label={`Accent: ${result.voice_characteristics.accent}`} size="small" />
                    </Grid>
                    <Grid item xs={12}>
                      <Chip label={`Speaking Rate: ${result.voice_characteristics.speaking_rate}`} size="small" />
                    </Grid>
                  </Grid>

                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>Analysis Details:</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Duration: {result.analysis_details.audio_duration} | 
                    Quality: {result.analysis_details.audio_quality} | 
                    Clarity: {result.analysis_details.speech_clarity}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ) : (
            <Alert severity="warning" icon={<Error />}>
              No voice match found in database
            </Alert>
          )}
        </Paper>
      )}
    </Box>
  )
}
