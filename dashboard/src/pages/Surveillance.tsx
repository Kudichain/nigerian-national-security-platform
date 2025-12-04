import { useState, useEffect, useRef } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  MenuItem,
  CircularProgress,
} from '@mui/material'
import {
  Videocam,
  MyLocation,
  LocalFireDepartment,
  DirectionsCar,
  Group,
  Warning,
  FlightTakeoff,
  Traffic,
  Search,
  PlayArrow,
} from '@mui/icons-material'
import { Loader } from '@googlemaps/js-api-loader'

interface Camera {
  camera_id: string
  name: string
  location: {
    lat: number
    lng: number
    address: string
    city: string
    state: string
  }
  stream_url: string
  camera_type: string
  status: string
  ai_enabled: boolean
  owner?: string
}

interface VideoEvent {
  event_id: string
  camera_id: string
  timestamp: string
  event_type: string
  confidence: number
  location: {
    lat: number
    lng: number
    city: string
  }
  metadata: Record<string, unknown>
  snapshot_url?: string
}

interface SearchResult {
  camera: Camera
  event: VideoEvent
}

const EVENT_ICONS: Record<string, React.ReactNode> = {
  vehicle_detection: <DirectionsCar />,
  crowd_detection: <Group />,
  fire_smoke: <LocalFireDepartment />,
  violence: <Warning />,
  drone_detection: <FlightTakeoff />,
  accident: <Traffic />,
  riot: <Warning />,
}

const EVENT_COLORS: Record<string, string> = {
  vehicle_detection: '#2196f3',
  crowd_detection: '#ff9800',
  fire_smoke: '#f44336',
  violence: '#d32f2f',
  drone_detection: '#9c27b0',
  accident: '#ff5722',
  riot: '#c62828',
}

export default function Surveillance() {
  const mapRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [cameras, setCameras] = useState<Camera[]>([])
  const [events, setEvents] = useState<VideoEvent[]>([])
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null)
  const [searchCity, setSearchCity] = useState('Abuja')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [, setMarkers] = useState<google.maps.Marker[]>([])

  // Initialize Google Maps
  useEffect(() => {
    const loader = new Loader({
      apiKey: 'YOUR_GOOGLE_MAPS_API_KEY', // Replace with actual API key
      version: 'weekly',
    })

    // @ts-expect-error - Loader API compatibility
    loader.load().then(() => {
      if (!mapRef.current) {
        return
      }

      const googleMap = new google.maps.Map(mapRef.current, {
        center: { lat: 9.0765, lng: 7.4890 }, // Abuja, Nigeria
        zoom: 12,
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true,
      })

      setMap(googleMap)
    })
  }, [])

  // Load cameras
  useEffect(() => {
    fetchCameras()
    fetchEvents()
    const interval = setInterval(() => {
      fetchEvents()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  // Update map markers when cameras load
  useEffect(() => {
    if (!map) {
      return
    }

    if (cameras.length === 0) {
      setMarkers((previousMarkers) => {
        previousMarkers.forEach((marker) => marker.setMap(null))
        return []
      })
      return
    }

    const newMarkers = cameras.map((camera) => {
      const marker = new google.maps.Marker({
        position: { lat: camera.location.lat, lng: camera.location.lng },
        map,
        title: camera.name,
        icon: {
          url:
            'data:image/svg+xml;utf-8,' +
            encodeURIComponent(`
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" fill="${camera.status === 'online' ? '#4caf50' : '#f44336'}"/>
                <text x="12" y="16" text-anchor="middle" fill="white" font-size="12">📹</text>
              </svg>
            `),
          scaledSize: new google.maps.Size(30, 30),
        },
      })

      marker.addListener('click', () => {
        setSelectedCamera(camera)
      })

      return marker
    })

    setMarkers((previousMarkers) => {
      previousMarkers.forEach((marker) => marker.setMap(null))
      return newMarkers
    })
  }, [map, cameras])

  const fetchCameras = async () => {
    try {
      const response = await fetch('http://localhost:8091/api/v1/cameras')
      if (!response.ok) {
        throw new Error('Failed to fetch cameras')
      }
      const data = (await response.json()) as Camera[]
      setCameras(data)
    } catch (error) {
      console.error('Failed to fetch cameras:', error)
    }
  }

  const fetchEvents = async () => {
    try {
      const response = await fetch('http://localhost:8091/api/v1/events?limit=50')
      if (!response.ok) {
        throw new Error('Failed to fetch events')
      }
      const data = (await response.json()) as VideoEvent[]
      setEvents(data)
    } catch (error) {
      console.error('Failed to fetch events:', error)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery) return

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8091/api/v1/surveillance/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          city: searchCity,
          query: searchQuery,
          time_range: 'last_24_hours',
          min_confidence: 0.7,
        }),
      })
      if (!response.ok) {
        throw new Error('Failed to perform search')
      }
      const data = (await response.json()) as SearchResult[]
      setSearchResults(data)

      // Zoom to first result if exists
      if (data.length > 0 && map) {
        const firstResult = data[0]
        map.setCenter({ lat: firstResult.event.location.lat, lng: firstResult.event.location.lng })
        map.setZoom(15)
      }
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const cameraStats = {
    total: cameras.length,
    online: cameras.filter((c) => c.status === 'online').length,
    offline: cameras.filter((c) => c.status === 'offline').length,
    aiEnabled: cameras.filter((c) => c.ai_enabled).length,
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        City Surveillance - Live Camera Network
      </Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight="bold">
          LEGAL NOTICE: Privacy-Compliant Video Monitoring
        </Typography>
        <Typography variant="body2">
          Video analysis for public safety only (NDPR 2019, Lagos State CCTV Law 2021). No facial recognition without
          warrant. All access logged.
        </Typography>
      </Alert>

      {/* Camera Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #2196f3' }}>
            <CardContent>
              <Typography variant="h4">{cameraStats.total}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Cameras
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #4caf50' }}>
            <CardContent>
              <Typography variant="h4" color="success.main">
                {cameraStats.online}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Online
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #f44336' }}>
            <CardContent>
              <Typography variant="h4" color="error.main">
                {cameraStats.offline}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Offline
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #9c27b0' }}>
            <CardContent>
              <Typography variant="h4">{cameraStats.aiEnabled}</Typography>
              <Typography variant="body2" color="text.secondary">
                AI-Enabled
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Map */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              <MyLocation sx={{ verticalAlign: 'middle', mr: 1 }} />
              Live Camera Map (Google Maps API)
            </Typography>
            <Box ref={mapRef} sx={{ width: '100%', height: 500, borderRadius: 1, overflow: 'hidden' }} />
          </Paper>

          {/* Search */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Search sx={{ verticalAlign: 'middle', mr: 1 }} />
              Surveillance Search
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  select
                  fullWidth
                  label="City"
                  value={searchCity}
                  onChange={(e) => setSearchCity(e.target.value)}
                >
                  <MenuItem value="Abuja">Abuja</MenuItem>
                  <MenuItem value="Lagos">Lagos</MenuItem>
                  <MenuItem value="Port Harcourt">Port Harcourt</MenuItem>
                  <MenuItem value="Kano">Kano</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={5}>
                <TextField
                  fullWidth
                  label="Search Query"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="red toyota camry, crowd gathering, fire"
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} /> : <Search />}
                  onClick={handleSearch}
                  disabled={loading}
                >
                  Search
                </Button>
              </Grid>
            </Grid>

            {searchResults.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Found {searchResults.length} matches
                </Typography>
                <List>
                  {searchResults.slice(0, 5).map((result) => (
                    <ListItem
                      key={result.event.event_id}
                      sx={{
                        bgcolor: 'rgba(33, 150, 243, 0.1)',
                        borderRadius: 1,
                        mb: 1,
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'rgba(33, 150, 243, 0.2)' },
                      }}
                      onClick={() => {
                        if (map) {
                          map.setCenter({ lat: result.event.location.lat, lng: result.event.location.lng })
                          map.setZoom(16)
                        }
                      }}
                    >
                      <ListItemIcon>{EVENT_ICONS[result.event.event_type] || <Videocam />}</ListItemIcon>
                      <ListItemText
                        primary={`${result.camera.name} - ${result.event.event_type.replace(/_/g, ' ').toUpperCase()}`}
                        secondary={`${new Date(result.event.timestamp).toLocaleString()} | Confidence: ${(result.event.confidence * 100).toFixed(0)}%`}
                      />
                      <Chip
                        label={`${(result.event.confidence * 100).toFixed(0)}%`}
                        size="small"
                        color={result.event.confidence > 0.85 ? 'error' : 'warning'}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Events & Cameras List */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent AI Events
            </Typography>
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {events.slice(0, 10).map((event) => (
                <ListItem
                  key={event.event_id}
                  sx={{
                    borderLeft: `4px solid ${EVENT_COLORS[event.event_type] || '#9e9e9e'}`,
                    mb: 1,
                    bgcolor: 'rgba(255,255,255,0.05)',
                    borderRadius: 1,
                  }}
                >
                  <ListItemIcon>{EVENT_ICONS[event.event_type] || <Warning />}</ListItemIcon>
                  <ListItemText
                    primary={event.event_type.replace(/_/g, ' ').toUpperCase()}
                    secondary={
                      <>
                        {new Date(event.timestamp).toLocaleTimeString()}
                        <br />
                        Confidence: {(event.confidence * 100).toFixed(0)}%
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Camera List
            </Typography>
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {cameras.map((camera) => (
                <ListItem
                  key={camera.camera_id}
                  sx={{
                    cursor: 'pointer',
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' },
                  }}
                  onClick={() => {
                    setSelectedCamera(camera)
                    if (map) {
                      map.setCenter({ lat: camera.location.lat, lng: camera.location.lng })
                      map.setZoom(16)
                    }
                  }}
                >
                  <ListItemIcon>
                    <Videocam color={camera.status === 'online' ? 'success' : 'error'} />
                  </ListItemIcon>
                  <ListItemText primary={camera.name} secondary={camera.location.address} />
                  <Chip label={camera.status.toUpperCase()} size="small" color={camera.status === 'online' ? 'success' : 'error'} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Camera Details Dialog */}
      <Dialog open={!!selectedCamera} onClose={() => setSelectedCamera(null)} maxWidth="md" fullWidth>
        {selectedCamera && (
          <>
            <DialogTitle>
              <Videocam sx={{ verticalAlign: 'middle', mr: 1 }} />
              {selectedCamera.name}
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Alert severity="info">
                    <Typography variant="subtitle2" fontWeight="bold">
                      Camera Information
                    </Typography>
                    <Typography variant="body2">
                      ID: {selectedCamera.camera_id}
                      <br />
                      Type: {selectedCamera.camera_type.toUpperCase()}
                      <br />
                      Location: {selectedCamera.location.address}
                      <br />
                      Owner: {selectedCamera.owner || 'Unknown'}
                    </Typography>
                  </Alert>
                </Grid>
                <Grid item xs={12}>
                  <Box
                    sx={{
                      width: '100%',
                      height: 400,
                      bgcolor: '#000',
                      borderRadius: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fff',
                    }}
                  >
                    <Box sx={{ textAlign: 'center' }}>
                      <Videocam sx={{ fontSize: 80, mb: 2 }} />
                      <Typography variant="h6">Live Feed Placeholder</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Integrate with RTSP stream: {selectedCamera.stream_url}
                      </Typography>
                      <Button variant="contained" startIcon={<PlayArrow />} sx={{ mt: 2 }}>
                        Request Live Feed Access
                      </Button>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedCamera(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}
