import { useState } from 'react'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Badge,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Warning as WarningIcon,
  Search as SearchIcon,
  Insights as InsightsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  FiberManualRecord as StatusIcon,
  AccountBalance as AccountBalanceIcon,
  Fingerprint as FingerprintIcon,
  FlightTakeoff as FlightTakeoffIcon,
  PersonSearch as PersonSearchIcon,
  Videocam as VideocamIcon,
  Map as MapIcon,
  Traffic as TrafficIcon,
  Water as WaterIcon,
  DirectionsCar as DirectionsCarIcon,
  ConnectedTv as ConnectedTvIcon,
  CardTravel as CardTravelIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  PhotoCamera as PhotoCameraIcon,
  Phone as PhoneIcon,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useAlertStore } from '../store/alertStore'
import { useEffect } from 'react'

const drawerWidth = 260

interface Props {
  children: React.ReactNode
}

export default function Layout({ children }: Props) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { alerts, connected, connectWebSocket, disconnectWebSocket } = useAlertStore()

  const newAlertsCount = alerts.filter((alert) => alert.status === 'new').length

  useEffect(() => {
    connectWebSocket()
    return () => disconnectWebSocket()
  }, [connectWebSocket, disconnectWebSocket])

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/', section: 'main' },
    { text: 'Alerts', icon: <WarningIcon />, path: '/alerts', badge: newAlertsCount, section: 'main' },
    { text: 'Investigation', icon: <SearchIcon />, path: '/investigation', section: 'main' },
    { text: 'AI Insights', icon: <InsightsIcon />, path: '/insights', section: 'main' },
    { text: 'Agencies', icon: <AccountBalanceIcon />, path: '/agencies', section: 'main' },
    { text: 'Identity', icon: <FingerprintIcon />, path: '/identity', section: 'verification' },
    { text: 'Visa Verification', icon: <CardTravelIcon />, path: '/visa-verification', section: 'verification' },
    { text: 'Voice Verification', icon: <RecordVoiceOverIcon />, path: '/voice-verification', section: 'verification' },
    { text: 'Photo Verification', icon: <PhotoCameraIcon />, path: '/photo-verification', section: 'verification' },
    { text: 'Phone Tracking', icon: <PhoneIcon />, path: '/phone-tracking', section: 'verification' },
    { text: 'Citizen Search', icon: <PersonSearchIcon />, path: '/citizen-search', section: 'search' },
    { text: 'Vehicle Tracking', icon: <DirectionsCarIcon />, path: '/vehicle-tracking', section: 'tracking' },
    { text: 'Security Map', icon: <MapIcon />, path: '/security-map', section: 'monitoring' },
    { text: 'Infrastructure', icon: <WaterIcon />, path: '/infrastructure', section: 'monitoring' },
    { text: 'CCTV Monitoring', icon: <VideocamIcon />, path: '/cctv', section: 'monitoring' },
    { text: 'Border CCTV', icon: <VideocamIcon />, path: '/border-cctv', section: 'monitoring' },
    { text: 'Toll Gate CCTV', icon: <TrafficIcon />, path: '/tollgate-cctv', section: 'monitoring' },
    { text: 'Drone Live', icon: <FlightTakeoffIcon />, path: '/drone-live', section: 'monitoring' },
    { text: 'City Surveillance', icon: <ConnectedTvIcon />, path: '/city-surveillance', section: 'monitoring' },
    { text: 'Surveillance', icon: <TrafficIcon />, path: '/surveillance', section: 'monitoring' },
    { text: 'Airport Pilot', icon: <FlightTakeoffIcon />, path: '/pilot', section: 'special' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings', section: 'settings' },
  ]

  const drawer = (
    <Box sx={{ backgroundColor: '#0a1929', height: '100%', color: '#fff' }}>
      <Toolbar sx={{ backgroundColor: '#001e3c', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 700, color: '#66b2ff' }}>
          🇳🇬 Security AI
        </Typography>
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)' }} />
      
      {/* Main Section */}
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
          Main
        </Typography>
      </Box>
      <List sx={{ py: 0 }}>
        {menuItems.filter(item => item.section === 'main').map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(102, 178, 255, 0.15)',
                  borderLeft: '3px solid #66b2ff',
                },
                '&:hover': {
                  backgroundColor: 'rgba(102, 178, 255, 0.08)',
                },
                color: '#fff',
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? '#66b2ff' : 'rgba(255,255,255,0.7)', minWidth: 40 }}>
                {item.badge ? (
                  <Badge badgeContent={item.badge} color="error">
                    {item.icon}
                  </Badge>
                ) : (
                  item.icon
                )}
              </ListItemIcon>
              <ListItemText primary={item.text} sx={{ '& .MuiTypography-root': { fontSize: '0.875rem' } }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      {/* Verification Section */}
      <Box sx={{ px: 2, py: 1, mt: 1 }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
          Verification
        </Typography>
      </Box>
      <List sx={{ py: 0 }}>
        {menuItems.filter(item => item.section === 'verification').map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(102, 178, 255, 0.15)',
                  borderLeft: '3px solid #66b2ff',
                },
                '&:hover': {
                  backgroundColor: 'rgba(102, 178, 255, 0.08)',
                },
                color: '#fff',
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? '#66b2ff' : 'rgba(255,255,255,0.7)', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} sx={{ '& .MuiTypography-root': { fontSize: '0.875rem' } }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      {/* Monitoring Section */}
      <Box sx={{ px: 2, py: 1, mt: 1 }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
          Monitoring
        </Typography>
      </Box>
      <List sx={{ py: 0 }}>
        {menuItems.filter(item => item.section === 'monitoring').map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(102, 178, 255, 0.15)',
                  borderLeft: '3px solid #66b2ff',
                },
                '&:hover': {
                  backgroundColor: 'rgba(102, 178, 255, 0.08)',
                },
                color: '#fff',
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? '#66b2ff' : 'rgba(255,255,255,0.7)', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} sx={{ '& .MuiTypography-root': { fontSize: '0.875rem' } }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.1)', mt: 2 }} />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={logout} sx={{ color: '#fff', '&:hover': { backgroundColor: 'rgba(244, 67, 54, 0.15)' } }}>
            <ListItemIcon sx={{ color: '#f44336', minWidth: 40 }}>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Logout" sx={{ '& .MuiTypography-root': { fontSize: '0.875rem' } }} />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Security AI Platform
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <StatusIcon
                sx={{ fontSize: 12 }}
                color={connected ? 'success' : 'error'}
              />
              <Typography variant="body2">
                {connected ? 'Connected' : 'Disconnected'}
              </Typography>
            </Box>
            <Typography variant="body2">
              {user?.username} ({user?.role})
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        {children}
      </Box>
    </Box>
  )
}
