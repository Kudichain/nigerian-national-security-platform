/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from 'react'
import { Box, Paper, Typography, Button, Grid, Card, CardContent, Avatar, Chip, CircularProgress, Alert } from '@mui/material'
import { PhotoCamera, CloudUpload, Error } from '@mui/icons-material'

export default function PhotoVerification() {
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [result, setResult] = useState<Record<string, any> | null>(null)
  const [loading, setLoading] = useState(false)

  const handleFileChange = (file: File | null) => {
    setPhotoFile(file)
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => setPreview(reader.result as string)
      reader.readAsDataURL(file)
    } else {
      setPreview(null)
    }
  }

  const handleVerify = async () => {
    if (!photoFile) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', photoFile)
      
      const response = await fetch('http://localhost:8000/api/v1/photo/verify', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ error: 'Failed to verify photo. Please ensure service is running.' })
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'success'
    if (confidence >= 75) return 'warning'
    return 'error'
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <PhotoCamera sx={{ fontSize: 40 }} /> Photo Verification System
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Facial recognition search to identify citizens from photos
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUpload />}
              fullWidth
              sx={{ height: 120, borderStyle: 'dashed', borderWidth: 2 }}
            >
              {photoFile ? 'Change Photo' : 'Upload Photo (JPG, PNG)'}
              <input
                type="file"
                hidden
                accept="image/*"
                onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              />
            </Button>
          </Grid>
          {preview && (
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                height: 120, 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                overflow: 'hidden'
              }}>
                <Box
                  component="img"
                  src={preview}
                  alt="Preview"
                  sx={{ maxHeight: '100%', maxWidth: '100%' }}
                />
              </Box>
            </Grid>
          )}
          <Grid item xs={12}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handleVerify}
              disabled={!photoFile || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <PhotoCamera />}
            >
              {loading ? 'Searching...' : 'Search Citizens'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {result && !loading && (
        <Paper sx={{ p: 3 }}>
          {result.error ? (
            <Alert severity="error">{result.error}</Alert>
          ) : result.matches && result.matches.length > 0 ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                Found {result.total_matches} Match{result.total_matches !== 1 ? 'es' : ''}
              </Typography>
              <Grid container spacing={2}>
                {result.matches.map((match: any, index: number) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                          <Avatar src={match.photo} sx={{ width: 64, height: 64 }} />
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="h6">{match.name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              NIN: {match.nin}
                            </Typography>
                            <Chip 
                              label={`${match.confidence}% Confidence`}
                              size="small"
                              color={getConfidenceColor(match.confidence)}
                              sx={{ mt: 1 }}
                            />
                          </Box>
                        </Box>
                        <Typography variant="body2">
                          📍 {match.location} | {match.age} years, {match.gender}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last seen: {match.last_seen}
                        </Typography>
                        <Button size="small" fullWidth sx={{ mt: 2 }}>
                          View Full Profile
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          ) : (
            <Alert severity="warning" icon={<Error />}>
              No faces found in photo
            </Alert>
          )}
        </Paper>
      )}
    </Box>
  )
}
