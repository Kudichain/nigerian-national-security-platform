import { useState, useEffect, useRef } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Paper,
  Stack,
  Divider,
  IconButton,
  Badge,
  TextField,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
} from '@mui/material'
import {
  Videocam,
  MyLocation,
  Search,
  Layers,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Refresh,
  PlayCircle,
  FlightTakeoff,
  DirectionsCar,
} from '@mui/icons-material'

interface Camera {
  id: string
  label: string
  type: 'traffic' | 'airport' | 'drone' | 'city'
  location: string
  lat: number
  lng: number
  hls?: string
  status: 'online' | 'offline' | 'maintenance'
  resolution: string
  fps: number
  lastSeen?: string
}


// Note: Google Maps API key removed - using mock map display
// To enable real maps, add your API key at the top of the file

// Mock video player component
const VideoPlayer = ({ streamUrl }: { streamUrl?: string; title: string }) => (
  <Box
    sx={{
      width: '100%',
      height: 400,
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
      borderRadius: 2,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      overflow: 'hidden',
    }}
  >
    {streamUrl ? (
      <Box
        component="video"
        src={streamUrl}
        controls
        autoPlay
        muted
        sx={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
    ) : (
      <Box sx={{ textAlign: 'center' }}>
        <Videocam sx={{ fontSize: 80, opacity: 0.5, mb: 2 }} />
        <Typography>Camera Offline - No Stream Available</Typography>
      </Box>
    )}
  </Box>
)

// Mock camera data for Nigerian cities
const mockCameras: Camera[] = [
  {
    id: 'cam-abuja-ibb',
    label: 'IBB Way Intersection',
    type: 'traffic',
    location: 'Abuja - Central Business District',
    lat: 9.0765,
    lng: 7.3986,
    hls: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    status: 'online',
    resolution: '1920x1080',
    fps: 30,
    lastSeen: '1 min ago',
  },
  {
    id: 'cam-abuja-airport',
    label: 'Airport Road Main Gate',
    type: 'airport',
    location: 'Abuja - Nnamdi Azikiwe Airport',
    lat: 9.0068,
    lng: 7.2631,
    hls: 'https://test-streams.mux.dev/pts_shift.m3u8',
    status: 'online',
    resolution: '2560x1440',
    fps: 60,
    lastSeen: '30 sec ago',
  },
  {
    id: 'cam-lagos-vi',
    label: 'Victoria Island Roundabout',
    type: 'traffic',
    location: 'Lagos - Victoria Island',
    lat: 6.4281,
    lng: 3.4219,
    hls: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    status: 'online',
    resolution: '1920x1080',
    fps: 30,
    lastSeen: '2 min ago',
  },
  {
    id: 'cam-lagos-lekki',
    label: 'Lekki Toll Gate',
    type: 'traffic',
    location: 'Lagos - Lekki Phase 1',
    lat: 6.4474,
    lng: 3.4647,
    status: 'maintenance',
    resolution: '1920x1080',
    fps: 30,
    lastSeen: '1 hour ago',
  },
  {
    id: 'cam-kano-city',
    label: 'Kano City Center',
    type: 'city',
    location: 'Kano - Sabon Gari',
    lat: 12.0022,
    lng: 8.5920,
    hls: 'https://test-streams.mux.dev/pts_shift.m3u8',
    status: 'online',
    resolution: '1920x1080',
    fps: 30,
    lastSeen: '45 sec ago',
  },
  {
    id: 'cam-portharcourt-oil',
    label: 'Oil Field Monitoring',
    type: 'city',
    location: 'Port Harcourt - Industrial Zone',
    lat: 4.8156,
    lng: 7.0498,
    status: 'offline',
    resolution: '3840x2160',
    fps: 60,
    lastSeen: '5 hours ago',
  },
  {
    id: 'drone-abuja-patrol',
    label: 'Abuja Patrol Drone',
    type: 'drone',
    location: 'Abuja - Garki District',
    lat: 9.0420,
    lng: 7.4910,
    hls: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    status: 'online',
    resolution: '2560x1440',
    fps: 60,
    lastSeen: '10 sec ago',
  },
]

export default function CitySurveillance() {
  const [cameras] = useState<Camera[]>(mockCameras)
  const [selected, setSelected] = useState<Camera | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [cameraTypes, setCameraTypes] = useState<string[]>(['traffic', 'airport', 'drone', 'city'])
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const mapRef = useRef<HTMLDivElement>(null)

  // Initialize with first online camera on mount
  useEffect(() => {
    const firstOnline = cameras.find((c) => c.status === 'online')
    if (firstOnline && !selected) {
      setSelected(firstOnline)
    }
  }, [cameras, selected])

  const handleTypeToggle = (_event: React.MouseEvent<HTMLElement>, newTypes: string[]) => {
    if (newTypes.length > 0) {
      setCameraTypes(newTypes)
    }
  }

  const handleRefresh = () => {
    setLastUpdate(new Date())
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success'
      case 'maintenance':
        return 'warning'
      case 'offline':
        return 'error'
      default:
        return 'default'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle />
      case 'maintenance':
        return <Warning />
      case 'offline':
        return <ErrorIcon />
      default:
        return <Videocam />
    }
  }

  const filteredCameras = cameras.filter(
    (cam) =>
      cameraTypes.includes(cam.type) &&
      (cam.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cam.location.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const onlineCameras = filteredCameras.filter((c) => c.status === 'online').length

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            🌆 City Surveillance
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time camera feeds across Nigerian cities
          </Typography>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip
            icon={<Videocam />}
            label={`${onlineCameras} / ${filteredCameras.length} Online`}
            color={onlineCameras > 0 ? 'success' : 'error'}
            sx={{ fontWeight: 600 }}
          />
          <IconButton onClick={handleRefresh}>
            <Refresh />
          </IconButton>
        </Stack>
      </Box>

      <Grid container spacing={3}>
        {/* Left Sidebar - Camera List */}
        <Grid item xs={12} md={4} lg={3}>
          <Stack spacing={2}>
            {/* Search */}
            <TextField
              fullWidth
              placeholder="Search cameras..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />

            {/* Type Filter */}
            <Card>
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  <Layers sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
                  Camera Types
                </Typography>
                <ToggleButtonGroup
                  value={cameraTypes}
                  onChange={handleTypeToggle}
                  aria-label="camera types"
                  size="small"
                  sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}
                >
                  <ToggleButton value="traffic" aria-label="traffic" sx={{ flex: '1 1 45%' }}>
                    <DirectionsCar sx={{ mr: 0.5, fontSize: 18 }} />
                    Traffic
                  </ToggleButton>
                  <ToggleButton value="airport" aria-label="airport" sx={{ flex: '1 1 45%' }}>
                    <FlightTakeoff sx={{ mr: 0.5, fontSize: 18 }} />
                    Airport
                  </ToggleButton>
                  <ToggleButton value="drone" aria-label="drone" sx={{ flex: '1 1 45%' }}>
                    <FlightTakeoff sx={{ mr: 0.5, fontSize: 18 }} />
                    Drone
                  </ToggleButton>
                  <ToggleButton value="city" aria-label="city" sx={{ flex: '1 1 45%' }}>
                    <Videocam sx={{ mr: 0.5, fontSize: 18 }} />
                    City
                  </ToggleButton>
                </ToggleButtonGroup>
              </CardContent>
            </Card>

            {/* Camera List */}
            <Card>
              <CardContent sx={{ p: 1 }}>
                <List sx={{ p: 0, maxHeight: 500, overflow: 'auto' }}>
                  {filteredCameras.map((camera) => (
                    <ListItem key={camera.id} disablePadding sx={{ mb: 0.5 }}>
                      <ListItemButton
                        selected={selected?.id === camera.id}
                        onClick={() => {
                          setSelected(camera)
                        }}
                        sx={{
                          borderRadius: 1,
                          border: selected?.id === camera.id ? '2px solid' : '1px solid',
                          borderColor: selected?.id === camera.id ? 'primary.main' : 'divider',
                        }}
                      >
                        <ListItemIcon>
                          <Badge
                            variant="dot"
                            color={getStatusColor(camera.status)}
                            overlap="circular"
                          >
                            {camera.type === 'drone' ? <FlightTakeoff /> : <Videocam />}
                          </Badge>
                        </ListItemIcon>
                        <ListItemText
                          primary={camera.label}
                          secondary={
                            <Stack spacing={0.5} sx={{ mt: 0.5 }}>
                              <Typography variant="caption" color="text.secondary">
                                {camera.location}
                              </Typography>
                              <Chip
                                label={camera.status.toUpperCase()}
                                size="small"
                                color={getStatusColor(camera.status)}
                                icon={getStatusIcon(camera.status)}
                                sx={{ height: 20, fontSize: '0.65rem', fontWeight: 600, maxWidth: 'fit-content' }}
                              />
                            </Stack>
                          }
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Stack>
        </Grid>

        {/* Right Side - Map & Video */}
        <Grid item xs={12} md={8} lg={9}>
          <Stack spacing={2}>
            {/* Map */}
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MyLocation /> Camera Locations
                </Typography>
                <Box
                  ref={mapRef}
                  sx={{
                    height: 400,
                    width: '100%',
                    borderRadius: 2,
                    overflow: 'hidden',
                    border: '1px solid',
                    borderColor: 'divider',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                  }}
                >
                  <Box sx={{ textAlign: 'center' }}>
                    <MyLocation sx={{ fontSize: 60, mb: 2, opacity: 0.7 }} />
                    <Typography variant="h6">Camera Locations Map</Typography>
                    <Typography variant="body2" sx={{ opacity: 0.7, mt: 1 }}>
                      {filteredCameras.length} cameras active • Click to view
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Video Player */}
            {selected ? (
              <Card>
                <CardContent>
                  {selected.status === 'offline' && (
                    <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 2 }}>
                      This camera is currently offline. No live feed available.
                    </Alert>
                  )}
                  {selected.status === 'maintenance' && (
                    <Alert severity="warning" icon={<Warning />} sx={{ mb: 2 }}>
                      Camera is under maintenance. Stream may be intermittent.
                    </Alert>
                  )}

                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                        {selected.type === 'drone' ? <FlightTakeoff /> : <Videocam />}
                        {selected.label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {selected.location}
                      </Typography>
                    </Box>

                    <VideoPlayer
                      streamUrl={selected.hls}
                      title={selected.label}
                    />

                    <Divider />

                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="text.secondary">
                          Resolution
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {selected.resolution}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="text.secondary">
                          FPS
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {selected.fps} fps
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="text.secondary">
                          Type
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                          {selected.type}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="caption" color="text.secondary">
                          Last Seen
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {selected.lastSeen ?? 'Unknown'}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Stack>
                </CardContent>
              </Card>
            ) : (
              <Paper
                sx={{
                  p: 8,
                  textAlign: 'center',
                  background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
                  color: 'white',
                  minHeight: 300,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <PlayCircle sx={{ fontSize: 80, opacity: 0.3, mb: 2 }} />
                <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                  No Camera Selected
                </Typography>
                <Typography variant="body1" sx={{ opacity: 0.7 }}>
                  Select a camera from the list or click a marker on the map
                </Typography>
              </Paper>
            )}
          </Stack>
        </Grid>
      </Grid>

      {/* Last Update Time */}
      <Box sx={{ mt: 2, textAlign: 'right' }}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {lastUpdate.toLocaleTimeString()}
        </Typography>
      </Box>
    </Box>
  )
}
