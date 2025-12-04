import { useState, useEffect } from 'react'
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
  Alert,
  IconButton,
  Badge,
  LinearProgress,
} from '@mui/material'
import {
  FlightTakeoff,
  Battery90,
  NetworkCheck,
  Speed,
  Height,
  Refresh,
  Warning,
} from '@mui/icons-material'
import VideoPlayer from '../components/VideoPlayer'

interface Drone {
  id: string
  label: string
  location: string
  hls?: string
  webrtcOffer?: string
  status: 'online' | 'offline' | 'standby' | 'maintenance'
  battery?: number
  altitude?: number
  speed?: number
  operator?: string
  mission?: string
  coordinates?: { lat: number; lng: number }
}

// Mock drone data for Nigeria
const mockDrones: Drone[] = [
  {
    id: 'drone-abuja-alpha',
    label: 'Abuja Alpha',
    location: 'Central Business District',
    hls: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    status: 'online',
    battery: 87,
    altitude: 120,
    speed: 15,
    operator: 'Officer Adebayo',
    mission: 'Traffic monitoring - Garki area',
    coordinates: { lat: 9.0765, lng: 7.3986 },
  },
  {
    id: 'drone-lagos-scout',
    label: 'Lagos Scout',
    location: 'Victoria Island',
    hls: 'https://test-streams.mux.dev/pts_shift.m3u8',
    status: 'online',
    battery: 65,
    altitude: 95,
    speed: 12,
    operator: 'Officer Okafor',
    mission: 'Coastal patrol',
    coordinates: { lat: 6.4281, lng: 3.4219 },
  },
  {
    id: 'drone-kano-eagle',
    label: 'Kano Eagle',
    location: 'Kano City Center',
    hls: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    status: 'standby',
    battery: 100,
    altitude: 0,
    speed: 0,
    operator: 'Officer Ibrahim',
    mission: 'Standby - awaiting deployment',
    coordinates: { lat: 12.0022, lng: 8.5920 },
  },
  {
    id: 'drone-portharcourt-delta',
    label: 'Port Harcourt Delta',
    location: 'Oil Fields Region',
    status: 'offline',
    battery: 0,
    altitude: 0,
    speed: 0,
    operator: 'Officer Eze',
    mission: 'Maintenance - battery replacement',
    coordinates: { lat: 4.8156, lng: 7.0498 },
  },
]

export default function DroneLive() {
  const [drones, setDrones] = useState<Drone[]>(mockDrones)
  const [selected, setSelected] = useState<Drone | null>(null)
  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  useEffect(() => {
    // Auto-select first online drone
    const firstOnline = drones.find((d) => d.status === 'online')
    if (firstOnline && !selected) {
      setSelected(firstOnline)
    }

    // Auto-refresh drone telemetry every 5 seconds
    const interval = setInterval(() => {
      setLastUpdate(new Date())
      // Simulate telemetry updates
      setDrones((prev) =>
        prev.map((d) => ({
          ...d,
          battery: d.status === 'online' && d.battery ? Math.max(0, d.battery - Math.random() * 2) : d.battery,
          altitude: d.status === 'online' && d.altitude ? d.altitude + (Math.random() - 0.5) * 10 : d.altitude,
          speed: d.status === 'online' && d.speed ? Math.max(0, d.speed + (Math.random() - 0.5) * 3) : d.speed,
        }))
      )
    }, 5000)

    return () => clearInterval(interval)
  }, [drones, selected])

  const handleRefresh = () => {
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setLoading(false)
      setLastUpdate(new Date())
    }, 1000)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success'
      case 'standby':
        return 'warning'
      case 'offline':
      case 'maintenance':
        return 'error'
      default:
        return 'default'
    }
  }

  const onlineDrones = drones.filter((d) => d.status === 'online').length

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
            🚁 Drone Live Video
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time aerial surveillance and monitoring
          </Typography>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip
            icon={<FlightTakeoff />}
            label={`${onlineDrones} / ${drones.length} Online`}
            color={onlineDrones > 0 ? 'success' : 'error'}
            sx={{ fontWeight: 600 }}
          />
          <IconButton onClick={handleRefresh} disabled={loading}>
            <Refresh className={loading ? 'rotating' : ''} />
          </IconButton>
        </Stack>
      </Box>

      <Grid container spacing={3}>
        {/* Drone List Sidebar */}
        <Grid item xs={12} md={4} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <FlightTakeoff /> Available Drones
              </Typography>
              
              <List sx={{ p: 0 }}>
                {drones.map((drone) => (
                  <ListItem key={drone.id} disablePadding sx={{ mb: 1 }}>
                    <ListItemButton
                      selected={selected?.id === drone.id}
                      onClick={() => setSelected(drone)}
                      sx={{
                        borderRadius: 1,
                        border: selected?.id === drone.id ? '2px solid' : '1px solid',
                        borderColor: selected?.id === drone.id ? 'primary.main' : 'divider',
                      }}
                    >
                      <ListItemIcon>
                        <Badge
                          variant="dot"
                          color={getStatusColor(drone.status)}
                          overlap="circular"
                        >
                          <FlightTakeoff />
                        </Badge>
                      </ListItemIcon>
                      <ListItemText
                        primary={drone.label}
                        secondary={
                          <Stack spacing={0.5} sx={{ mt: 0.5 }}>
                            <Typography variant="caption" color="text.secondary">
                              {drone.location}
                            </Typography>
                            <Chip
                              label={drone.status.toUpperCase()}
                              size="small"
                              color={getStatusColor(drone.status)}
                              sx={{ height: 20, fontSize: '0.65rem', fontWeight: 600 }}
                            />
                          </Stack>
                        }
                        secondaryTypographyProps={{ component: 'div' }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Video Player & Telemetry */}
        <Grid item xs={12} md={8} lg={9}>
          {selected ? (
            <Stack spacing={2}>
              {/* Status Alert */}
              {selected.status === 'offline' && (
                <Alert severity="error" icon={<Warning />}>
                  This drone is currently offline. No live feed available.
                </Alert>
              )}
              {selected.status === 'standby' && (
                <Alert severity="warning" icon={<Warning />}>
                  Drone is on standby. Deploying will activate live feed.
                </Alert>
              )}

              {/* Video Player */}
              <Paper sx={{ p: 2 }}>
                <VideoPlayer
                  streamUrl={selected.hls}
                  rtcOfferUrl={selected.webrtcOffer}
                  title={selected.label}
                />
              </Paper>

              {/* Telemetry Dashboard */}
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    📊 Drone Telemetry
                  </Typography>
                  
                  <Grid container spacing={2}>
                    {/* Battery */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                        <Battery90 color={selected.battery && selected.battery > 20 ? 'success' : 'error'} sx={{ fontSize: 40 }} />
                        <Typography variant="h4" sx={{ fontWeight: 700, my: 1 }}>
                          {selected.battery?.toFixed(0) ?? 0}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Battery Level
                        </Typography>
                        {selected.battery && (
                          <LinearProgress
                            variant="determinate"
                            value={selected.battery}
                            color={selected.battery > 20 ? 'success' : 'error'}
                            sx={{ mt: 1, height: 6, borderRadius: 1 }}
                          />
                        )}
                      </Paper>
                    </Grid>

                    {/* Altitude */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                        <Height color="primary" sx={{ fontSize: 40 }} />
                        <Typography variant="h4" sx={{ fontWeight: 700, my: 1 }}>
                          {selected.altitude?.toFixed(0) ?? 0}m
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Altitude (AGL)
                        </Typography>
                      </Paper>
                    </Grid>

                    {/* Speed */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                        <Speed color="info" sx={{ fontSize: 40 }} />
                        <Typography variant="h4" sx={{ fontWeight: 700, my: 1 }}>
                          {selected.speed?.toFixed(1) ?? 0}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Speed (m/s)
                        </Typography>
                      </Paper>
                    </Grid>

                    {/* Signal */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                        <NetworkCheck color="success" sx={{ fontSize: 40 }} />
                        <Typography variant="h4" sx={{ fontWeight: 700, my: 1 }}>
                          Excellent
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Signal Strength
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  <Divider sx={{ my: 2 }} />

                  {/* Mission Info */}
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Stack spacing={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Operator
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                          {selected.operator}
                        </Typography>
                      </Stack>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Stack spacing={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Mission
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                          {selected.mission}
                        </Typography>
                      </Stack>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Stack spacing={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Location
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 600 }}>
                          {selected.location}
                        </Typography>
                      </Stack>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Stack spacing={1}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Coordinates
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                          {selected.coordinates?.lat.toFixed(4)}, {selected.coordinates?.lng.toFixed(4)}
                        </Typography>
                      </Stack>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Stack>
          ) : (
            <Paper
              sx={{
                p: 8,
                textAlign: 'center',
                background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
                color: 'white',
                minHeight: 500,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FlightTakeoff sx={{ fontSize: 80, opacity: 0.3, mb: 2 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                No Drone Selected
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.7 }}>
                Select a drone from the list to view its live feed and telemetry
              </Typography>
            </Paper>
          )}
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
