import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Investigation from './pages/Investigation'
import Insights from './pages/Insights'
import Settings from './pages/Settings'
import Login from './pages/Login'
import Agencies from './pages/Agencies'
import Identity from './pages/Identity'
import Pilot from './pages/Pilot'
import CitizenSearch from './pages/CitizenSearch'
import Surveillance from './pages/Surveillance'
import SecurityMap from './pages/SecurityMap'
import CCTVMonitoring from './pages/CCTVMonitoring'
import InfrastructureMonitoring from './pages/InfrastructureMonitoring'
import VehicleTracking from './pages/VehicleTracking'
import DroneLive from './pages/DroneLive'
import CitySurveillance from './pages/CitySurveillance'
import VisaVerification from './pages/VisaVerification'
import VoiceVerification from './pages/VoiceVerification'
import PhotoVerification from './pages/PhotoVerification'
import PhoneTracking from './pages/PhoneTracking'
import BorderCCTV from './pages/BorderCCTV'
import TollgateCCTV from './pages/TollgateCCTV'
import { useAuthStore } from './store/authStore'

function App() {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/investigation/:alertId" element={<Investigation />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/agencies" element={<Agencies />} />
          <Route path="/identity" element={<Identity />} />
          <Route path="/visa-verification" element={<VisaVerification />} />
          <Route path="/voice-verification" element={<VoiceVerification />} />
          <Route path="/photo-verification" element={<PhotoVerification />} />
          <Route path="/phone-tracking" element={<PhoneTracking />} />
          <Route path="/pilot" element={<Pilot />} />
          <Route path="/citizen-search" element={<CitizenSearch />} />
          <Route path="/surveillance" element={<Surveillance />} />
          <Route path="/security-map" element={<SecurityMap />} />
          <Route path="/cctv" element={<CCTVMonitoring />} />
          <Route path="/border-cctv" element={<BorderCCTV />} />
          <Route path="/tollgate-cctv" element={<TollgateCCTV />} />
          <Route path="/infrastructure" element={<InfrastructureMonitoring />} />
          <Route path="/vehicle-tracking" element={<VehicleTracking />} />
          <Route path="/drone-live" element={<DroneLive />} />
          <Route path="/city-surveillance" element={<CitySurveillance />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Box>
  )
}

export default App
