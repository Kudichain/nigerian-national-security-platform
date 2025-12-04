import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  TextField,
  Button,
  Chip,
  Stack,
  Paper,
  Alert,
  Divider,
  List,
  ListItem,
  Avatar,
  IconButton,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material'
import {
  DirectionsCar,
  Search,
  Warning,
  CheckCircle,
  Block,
  Report,
  Timeline,
  LocationOn,
  Person,
  DateRange,
  Description,
  Print,
  Share,
  Gavel,
  ErrorOutline,
} from '@mui/icons-material'

interface VehicleRecord {
  plateNumber: string
  state: string
  vehicleType: string
  make: string
  model: string
  year: number
  color: string
  engineNumber: string
  chassisNumber: string
  status: 'valid' | 'expired' | 'stolen' | 'wanted' | 'suspended'
  registrationDate: string
  expiryDate: string
  owner: {
    name: string
    nin: string
    phone: string
    address: string
    photo: string
  }
  violations: Array<{
    date: string
    offense: string
    location: string
    fine: number
    status: 'paid' | 'pending' | 'overdue'
  }>
  travelHistory: Array<{
    date: string
    location: string
    checkpoint: string
    officer: string
  }>
  watchStatus?: {
    reason: string
    reportedBy: string
    date: string
    severity: 'low' | 'medium' | 'high' | 'critical'
  }
}

// Mock vehicle database
const vehicleDatabase: { [key: string]: VehicleRecord } = {
  'ABC123LA': {
    plateNumber: 'ABC-123-LA',
    state: 'Lagos',
    vehicleType: 'Private Car',
    make: 'Toyota',
    model: 'Camry',
    year: 2022,
    color: 'Black',
    engineNumber: 'ENG2022ABC123',
    chassisNumber: 'CHS2022ABC123LA',
    status: 'valid',
    registrationDate: '2022-03-15',
    expiryDate: '2025-03-15',
    owner: {
      name: 'Adebayo Johnson',
      nin: '12345678901',
      phone: '+234 803 123 4567',
      address: '15 Victoria Island, Lagos',
      photo: 'https://i.pravatar.cc/150?img=12'
    },
    violations: [
      {
        date: '2024-09-10',
        offense: 'Speed Limit Violation',
        location: 'Lekki-Epe Expressway',
        fine: 15000,
        status: 'paid'
      }
    ],
    travelHistory: [
      {
        date: '2024-11-25',
        location: 'Abuja',
        checkpoint: 'Garki Police Checkpoint',
        officer: 'Inspector Musa'
      },
      {
        date: '2024-11-20',
        location: 'Lagos',
        checkpoint: 'Lekki Toll Gate',
        officer: 'Sergeant Obi'
      }
    ]
  },
  'XYZ789AB': {
    plateNumber: 'XYZ-789-AB',
    state: 'Abuja',
    vehicleType: 'SUV',
    make: 'Mercedes-Benz',
    model: 'GLE 450',
    year: 2021,
    color: 'White',
    engineNumber: 'ENG2021XYZ789',
    chassisNumber: 'CHS2021XYZ789AB',
    status: 'stolen',
    registrationDate: '2021-06-10',
    expiryDate: '2024-06-10',
    owner: {
      name: 'Mrs. Fatima Abdullahi',
      nin: '98765432109',
      phone: '+234 806 987 6543',
      address: '42 Maitama District, Abuja',
      photo: 'https://i.pravatar.cc/150?img=45'
    },
    violations: [],
    travelHistory: [],
    watchStatus: {
      reason: 'STOLEN - Armed robbery on 2024-11-15. Suspects armed and dangerous.',
      reportedBy: 'FCT Police Command',
      date: '2024-11-15',
      severity: 'critical'
    }
  },
  'DEF456KD': {
    plateNumber: 'DEF-456-KD',
    state: 'Kaduna',
    vehicleType: 'Commercial Taxi',
    make: 'Honda',
    model: 'Accord',
    year: 2019,
    color: 'Yellow',
    engineNumber: 'ENG2019DEF456',
    chassisNumber: 'CHS2019DEF456KD',
    status: 'wanted',
    registrationDate: '2019-02-20',
    expiryDate: '2024-02-20',
    owner: {
      name: 'Ibrahim Suleiman',
      nin: '45678901234',
      phone: '+234 802 345 6789',
      address: '78 Barnawa, Kaduna',
      photo: 'https://i.pravatar.cc/150?img=33'
    },
    violations: [
      {
        date: '2024-10-05',
        offense: 'Hit and Run',
        location: 'Kaduna-Abuja Highway',
        fine: 250000,
        status: 'pending'
      },
      {
        date: '2024-09-12',
        offense: 'Driving without valid license',
        location: 'Kaduna Central',
        fine: 50000,
        status: 'overdue'
      }
    ],
    travelHistory: [
      {
        date: '2024-11-24',
        location: 'Kaduna',
        checkpoint: 'Kaduna-Abuja Highway NDLEA',
        officer: 'Officer Yakubu'
      }
    ],
    watchStatus: {
      reason: 'WANTED - Hit and run accident resulting in serious injury. Driver fled scene.',
      reportedBy: 'Kaduna State Police',
      date: '2024-10-05',
      severity: 'high'
    }
  },
  'GHI789PH': {
    plateNumber: 'GHI-789-PH',
    state: 'Port Harcourt',
    vehicleType: 'Motorcycle',
    make: 'Bajaj',
    model: 'Boxer',
    year: 2023,
    color: 'Red',
    engineNumber: 'ENG2023GHI789',
    chassisNumber: 'CHS2023GHI789PH',
    status: 'suspended',
    registrationDate: '2023-01-10',
    expiryDate: '2026-01-10',
    owner: {
      name: 'Emeka Okoro',
      nin: '23456789012',
      phone: '+234 805 234 5678',
      address: '23 Trans Amadi, Port Harcourt',
      photo: 'https://i.pravatar.cc/150?img=68'
    },
    violations: [
      {
        date: '2024-11-01',
        offense: 'Multiple traffic violations',
        location: 'East-West Road',
        fine: 75000,
        status: 'overdue'
      },
      {
        date: '2024-10-15',
        offense: 'Reckless driving',
        location: 'Rumuokoro',
        fine: 30000,
        status: 'overdue'
      }
    ],
    travelHistory: [],
    watchStatus: {
      reason: 'SUSPENDED - License suspended due to multiple violations and unpaid fines',
      reportedBy: 'Rivers State FRSC',
      date: '2024-11-05',
      severity: 'medium'
    }
  }
}

export default function VehicleTracking() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResult, setSearchResult] = useState<VehicleRecord | null>(null)
  const [searchError, setSearchError] = useState('')
  const [activeTab, setActiveTab] = useState(0)

  const handleSearch = () => {
    setSearchError('')
    setSearchResult(null)

    if (!searchQuery.trim()) {
      setSearchError('Please enter a plate number')
      return
    }

    // Clean and format plate number
    const cleanPlate = searchQuery.toUpperCase().replace(/[^A-Z0-9]/g, '')
    
    // Search database
    const found = Object.values(vehicleDatabase).find(
      vehicle => vehicle.plateNumber.replace(/[^A-Z0-9]/g, '') === cleanPlate
    )

    if (found) {
      setSearchResult(found)
    } else {
      setSearchError('Vehicle not found in database. Please verify plate number.')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid': return 'success'
      case 'expired': return 'warning'
      case 'stolen': return 'error'
      case 'wanted': return 'error'
      case 'suspended': return 'warning'
      default: return 'default'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error'
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'default'
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
          🚗 Vehicle Tracking & License Verification
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Instant vehicle registration verification, stolen vehicle alerts, and traffic violation history
        </Typography>
      </Box>

      {/* Search Section */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField
              fullWidth
              placeholder="Enter plate number (e.g., ABC-123-LA)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              sx={{
                bgcolor: 'white',
                borderRadius: 1,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': { border: 'none' },
                },
              }}
              InputProps={{
                startAdornment: <DirectionsCar sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
            <Button
              variant="contained"
              size="large"
              onClick={handleSearch}
              startIcon={<Search />}
              sx={{
                minWidth: 150,
                bgcolor: 'white',
                color: 'primary.main',
                '&:hover': { bgcolor: 'grey.100' }
              }}
            >
              Search
            </Button>
          </Stack>

          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip 
              label="Try: ABC123LA" 
              size="small" 
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', cursor: 'pointer' }}
              onClick={() => setSearchQuery('ABC123LA')}
            />
            <Chip 
              label="Stolen: XYZ789AB" 
              size="small" 
              sx={{ bgcolor: 'rgba(255,0,0,0.3)', color: 'white', cursor: 'pointer' }}
              onClick={() => setSearchQuery('XYZ789AB')}
            />
            <Chip 
              label="Wanted: DEF456KD" 
              size="small" 
              sx={{ bgcolor: 'rgba(255,152,0,0.3)', color: 'white', cursor: 'pointer' }}
              onClick={() => setSearchQuery('DEF456KD')}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Error Message */}
      {searchError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {searchError}
        </Alert>
      )}

      {/* Search Results */}
      {searchResult && (
        <>
          {/* Critical Alert for Stolen/Wanted */}
          {(searchResult.status === 'stolen' || searchResult.status === 'wanted') && (
            <Alert 
              severity="error" 
              sx={{ mb: 3, border: 3, borderColor: 'error.main' }}
              icon={<ErrorOutline sx={{ fontSize: 32 }} />}
            >
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                🚨 {searchResult.status === 'stolen' ? 'STOLEN VEHICLE ALERT' : 'WANTED VEHICLE ALERT'}
              </Typography>
              <Typography variant="body1" sx={{ mb: 1 }}>
                {searchResult.watchStatus?.reason}
              </Typography>
              <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                <Button variant="contained" color="error" startIcon={<ErrorOutline />}>
                  DETAIN VEHICLE
                </Button>
                <Button variant="outlined" color="error" startIcon={<Gavel />}>
                  REPORT TO COMMAND
                </Button>
              </Stack>
            </Alert>
          )}

          {/* Vehicle Information */}
          <Grid container spacing={3}>
            {/* Left Column - Vehicle Details */}
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                    <Typography variant="h5" sx={{ fontWeight: 600 }}>
                      Vehicle Information
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small"><Print /></IconButton>
                      <IconButton size="small"><Share /></IconButton>
                    </Stack>
                  </Stack>

                  <Chip
                    label={searchResult.status.toUpperCase()}
                    color={getStatusColor(searchResult.status)}
                    icon={
                      searchResult.status === 'valid' ? <CheckCircle /> :
                      searchResult.status === 'stolen' || searchResult.status === 'wanted' ? <Block /> :
                      <Warning />
                    }
                    sx={{ mb: 2, fontWeight: 600 }}
                  />

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
                        <Typography variant="caption" color="text.secondary">
                          Plate Number
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                          {searchResult.plateNumber}
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Paper sx={{ p: 2, bgcolor: 'secondary.50' }}>
                        <Typography variant="caption" color="text.secondary">
                          State
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: 700, color: 'secondary.main' }}>
                          {searchResult.state}
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  <Divider sx={{ my: 2 }} />

                  <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
                    <Tab label="Details" icon={<Description />} iconPosition="start" />
                    <Tab label="Owner" icon={<Person />} iconPosition="start" />
                    <Tab label="Violations" icon={<Report />} iconPosition="start" />
                    <Tab label="Travel History" icon={<Timeline />} iconPosition="start" />
                  </Tabs>

                  {/* Tab 0: Vehicle Details */}
                  {activeTab === 0 && (
                    <Grid container spacing={2}>
                      {[
                        { label: 'Vehicle Type', value: searchResult.vehicleType },
                        { label: 'Make', value: searchResult.make },
                        { label: 'Model', value: searchResult.model },
                        { label: 'Year', value: searchResult.year },
                        { label: 'Color', value: searchResult.color },
                        { label: 'Engine Number', value: searchResult.engineNumber },
                        { label: 'Chassis Number', value: searchResult.chassisNumber },
                        { label: 'Registration Date', value: new Date(searchResult.registrationDate).toLocaleDateString() },
                        { label: 'Expiry Date', value: new Date(searchResult.expiryDate).toLocaleDateString() },
                      ].map((item, idx) => (
                        <Grid item xs={12} sm={6} key={idx}>
                          <Typography variant="caption" color="text.secondary">
                            {item.label}
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {item.value}
                          </Typography>
                        </Grid>
                      ))}
                    </Grid>
                  )}

                  {/* Tab 1: Owner Information */}
                  {activeTab === 1 && (
                    <Box>
                      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
                        <Avatar
                          src={searchResult.owner.photo}
                          sx={{ width: 80, height: 80 }}
                        />
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {searchResult.owner.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            NIN: {searchResult.owner.nin}
                          </Typography>
                        </Box>
                      </Stack>
                      <Grid container spacing={2}>
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">
                            Phone Number
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {searchResult.owner.phone}
                          </Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">
                            Address
                          </Typography>
                          <Typography variant="body1" sx={{ fontWeight: 600 }}>
                            {searchResult.owner.address}
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>
                  )}

                  {/* Tab 2: Violations */}
                  {activeTab === 2 && (
                    <Box>
                      {searchResult.violations.length === 0 ? (
                        <Alert severity="success">
                          <Typography>No traffic violations on record</Typography>
                        </Alert>
                      ) : (
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Date</TableCell>
                              <TableCell>Offense</TableCell>
                              <TableCell>Location</TableCell>
                              <TableCell>Fine (₦)</TableCell>
                              <TableCell>Status</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {searchResult.violations.map((violation, idx) => (
                              <TableRow key={idx}>
                                <TableCell>{new Date(violation.date).toLocaleDateString()}</TableCell>
                                <TableCell>{violation.offense}</TableCell>
                                <TableCell>{violation.location}</TableCell>
                                <TableCell>{violation.fine.toLocaleString()}</TableCell>
                                <TableCell>
                                  <Chip
                                    label={violation.status}
                                    size="small"
                                    color={
                                      violation.status === 'paid' ? 'success' :
                                      violation.status === 'overdue' ? 'error' : 'warning'
                                    }
                                  />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      )}
                    </Box>
                  )}

                  {/* Tab 3: Travel History */}
                  {activeTab === 3 && (
                    <List>
                      {searchResult.travelHistory.length === 0 ? (
                        <Alert severity="info">
                          <Typography>No travel history recorded</Typography>
                        </Alert>
                      ) : (
                        searchResult.travelHistory.map((travel, idx) => (
                          <ListItem key={idx} divider>
                            <Stack sx={{ width: '100%' }}>
                              <Stack direction="row" justifyContent="space-between">
                                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                  <LocationOn sx={{ fontSize: 16, verticalAlign: 'middle' }} />
                                  {travel.checkpoint}
                                </Typography>
                                <Chip label={new Date(travel.date).toLocaleDateString()} size="small" />
                              </Stack>
                              <Typography variant="body2" color="text.secondary">
                                {travel.location} • Officer: {travel.officer}
                              </Typography>
                            </Stack>
                          </ListItem>
                        ))
                      )}
                    </List>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Right Column - Watch Status & Quick Actions */}
            <Grid item xs={12} md={4}>
              <Stack spacing={2}>
                {/* Watch Status */}
                {searchResult.watchStatus && (
                  <Card sx={{ border: 2, borderColor: 'error.main' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Warning color="error" /> Watch Status
                      </Typography>
                      <Chip
                        label={`${searchResult.watchStatus.severity.toUpperCase()} SEVERITY`}
                        color={getSeverityColor(searchResult.watchStatus.severity)}
                        sx={{ mb: 2, fontWeight: 600 }}
                      />
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        {searchResult.watchStatus.reason}
                      </Typography>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="caption" color="text.secondary">
                        Reported By
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {searchResult.watchStatus.reportedBy}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                        Report Date
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {new Date(searchResult.watchStatus.date).toLocaleDateString()}
                      </Typography>
                    </CardContent>
                  </Card>
                )}

                {/* Quick Statistics */}
                <Card>
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Quick Statistics
                    </Typography>
                    <Stack spacing={2}>
                      <Paper sx={{ p: 1.5, bgcolor: 'warning.50' }}>
                        <Typography variant="caption" color="text.secondary">
                          Total Violations
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
                          {searchResult.violations.length}
                        </Typography>
                      </Paper>
                      <Paper sx={{ p: 1.5, bgcolor: 'error.50' }}>
                        <Typography variant="caption" color="text.secondary">
                          Outstanding Fines
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 700, color: 'error.main' }}>
                          ₦{searchResult.violations
                            .filter(v => v.status !== 'paid')
                            .reduce((sum, v) => sum + v.fine, 0)
                            .toLocaleString()}
                        </Typography>
                      </Paper>
                      <Paper sx={{ p: 1.5, bgcolor: 'info.50' }}>
                        <Typography variant="caption" color="text.secondary">
                          Checkpoint Records
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 700, color: 'info.main' }}>
                          {searchResult.travelHistory.length}
                        </Typography>
                      </Paper>
                    </Stack>
                  </CardContent>
                </Card>

                {/* Actions */}
                <Card>
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Actions
                    </Typography>
                    <Stack spacing={1}>
                      <Button variant="outlined" fullWidth startIcon={<Report />}>
                        Report Violation
                      </Button>
                      <Button variant="outlined" fullWidth startIcon={<DateRange />}>
                        Update Record
                      </Button>
                      <Button variant="outlined" fullWidth startIcon={<Print />}>
                        Print Report
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              </Stack>
            </Grid>
          </Grid>
        </>
      )}

      {/* No search yet */}
      {!searchResult && !searchError && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <DirectionsCar sx={{ fontSize: 120, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Enter a vehicle plate number to begin verification
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Instant access to registration status, owner details, and violation history
          </Typography>
        </Box>
      )}
    </Box>
  )
}
