import { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  MenuItem,
  CircularProgress,
  Divider,
} from '@mui/material'
import type { ChipProps } from '@mui/material'
import {
  Search,
  Person,
  Fingerprint,
  CreditCard,
  LocalAirport,
  CheckCircle,
  Error as ErrorIcon,
  Gavel,
  History,
} from '@mui/icons-material'

type SearchType = 'nin' | 'bvn' | 'passport' | 'phone' | 'name'

interface CitizenProfile {
  searchId: string
  timestamp: string
  officerId: string
  caseId: string
  searchType: SearchType
  matchScore: number
  nimcResult?: IdentityResult
  bvnResult?: IdentityResult
  passportResult?: IdentityResult
  linkedAlerts: string[]
  auditTrailId: string
}

type IdentityResult = Record<string, string | number | boolean | null | undefined>

export default function CitizenSearch() {
  const [searchType, setSearchType] = useState<SearchType>('nin')
  const [searchValue, setSearchValue] = useState('')
  const [officerId, setOfficerId] = useState('NPF-12345')
  const [caseId, setCaseId] = useState('')
  const [justification, setJustification] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CitizenProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [searchHistory, setSearchHistory] = useState<CitizenProfile[]>([])

  const handleSearch = async () => {
    if (!searchValue || !caseId || !justification) {
      setError('All fields are required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8090/api/v1/citizen/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_type: searchType,
          value: searchValue,
          officer_id: officerId,
          case_id: caseId,
          justification: justification,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Search failed')
      }

      const data = (await response.json()) as CitizenProfile
      setResult(data)
      setSearchHistory((prev) => [data, ...prev])
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Search failed'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const getMatchScoreColor = (score: number): ChipProps['color'] => {
    if (score >= 0.9) return 'success'
    if (score >= 0.7) return 'warning'
    return 'error'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Citizen Search - Federated Identity Verification
      </Typography>
      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight="bold">
          LEGAL NOTICE: Authorized Access Only
        </Typography>
        <Typography variant="body2">
          All searches are logged for NDPR 2019 compliance. Requires valid case ID and justification. Unauthorized
          access is a criminal offense under Cybercrime Act 2015.
        </Typography>
      </Alert>

      {/* Search Form */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Search Citizen Records
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              select
              fullWidth
              label="Search Type"
              value={searchType}
              onChange={(e) => setSearchType(e.target.value as SearchType)}
            >
              <MenuItem value="nin">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Fingerprint fontSize="small" />
                  National ID Number (NIN)
                </Box>
              </MenuItem>
              <MenuItem value="bvn">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CreditCard fontSize="small" />
                  Bank Verification Number (BVN)
                </Box>
              </MenuItem>
              <MenuItem value="passport">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocalAirport fontSize="small" />
                  International Passport
                </Box>
              </MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={`Enter ${searchType.toUpperCase()}`}
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder={
                searchType === 'nin'
                  ? '12345678901 (11 digits)'
                  : searchType === 'bvn'
                  ? '22339911001 (11 digits)'
                  : 'A12345678 (1 letter + 8 digits)'
              }
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Officer ID"
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value)}
              placeholder="NPF-12345 or DSS-98765"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Case ID"
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              placeholder="KIDNAP-20251127 or FRAUD-2025-0045"
              required
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Justification (Required for Audit)"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Describe why this search is necessary for the investigation (min 10 characters)"
              required
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <Search />}
              onClick={handleSearch}
              disabled={loading}
              fullWidth
            >
              {loading ? 'Searching...' : 'Search Citizen Records'}
            </Button>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {/* Search Results */}
      {result && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Search Results</Typography>
            <Chip
              label={`Match Score: ${(result.matchScore * 100).toFixed(0)}%`}
              color={getMatchScoreColor(result.matchScore)}
              size="medium"
            />
          </Box>

          {/* NIMC Result */}
          {result.nimcResult && result.nimcResult.match && (
            <Card sx={{ mb: 2, borderLeft: '4px solid #2196f3' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Avatar sx={{ bgcolor: '#2196f3', width: 80, height: 80 }}>
                    {result.nimcResult.photo_base64 ? (
                      <Box
                        component="img"
                        src={`data:image/png;base64,${result.nimcResult.photo_base64}`}
                        alt="Citizen"
                        sx={{ width: '100%', height: '100%' }}
                      />
                    ) : (
                      <Person fontSize="large" />
                    )}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6">{result.nimcResult.full_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Date of Birth: {result.nimcResult.date_of_birth}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Gender: {result.nimcResult.gender}
                    </Typography>
                  </Box>
                  <Chip label="NIMC VERIFIED" color="success" icon={<CheckCircle />} />
                </Box>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      State of Origin
                    </Typography>
                    <Typography variant="body2">{result.nimcResult.state_of_origin}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      LGA
                    </Typography>
                    <Typography variant="body2">{result.nimcResult.lga}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">
                      NIN Hash (Unlinkable Pseudonym)
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '11px' }}>
                      {typeof result.nimcResult.nin_hash === 'string' ? result.nimcResult.nin_hash.substring(0, 32) : result.nimcResult.nin_hash}...
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* BVN Result */}
          {result.bvnResult && result.bvnResult.match && (
            <Card sx={{ mb: 2, borderLeft: '4px solid #ff9800' }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  <CreditCard sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Bank Verification Number (CBN)
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Full Name
                    </Typography>
                    <Typography variant="body2">{result.bvnResult.full_name}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Phone Number
                    </Typography>
                    <Typography variant="body2">{result.bvnResult.phone_number}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Bank Accounts
                    </Typography>
                    <Typography variant="body2">{result.bvnResult.bank_count} accounts</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Registration Date
                    </Typography>
                    <Typography variant="body2">{result.bvnResult.registration_date}</Typography>
                  </Grid>
                </Grid>
                <Chip label="CBN VERIFIED" color="warning" icon={<CheckCircle />} sx={{ mt: 2 }} />
              </CardContent>
            </Card>
          )}

          {/* Passport Result */}
          {result.passportResult && result.passportResult.match && (
            <Card sx={{ mb: 2, borderLeft: '4px solid #4caf50' }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                  <LocalAirport sx={{ verticalAlign: 'middle', mr: 1 }} />
                  International Passport (Immigration)
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Full Name
                    </Typography>
                    <Typography variant="body2">{result.passportResult.full_name}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Nationality
                    </Typography>
                    <Typography variant="body2">{result.passportResult.nationality}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Issue Date
                    </Typography>
                    <Typography variant="body2">{result.passportResult.issue_date}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Expiry Date
                    </Typography>
                    <Typography variant="body2">{result.passportResult.expiry_date}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Travel History
                    </Typography>
                    <Typography variant="body2">{result.passportResult.travel_history_count} trips</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Watchlist Status
                    </Typography>
                    <Chip
                      label={typeof result.passportResult.watchlist_status === 'string' ? result.passportResult.watchlist_status.toUpperCase() : String(result.passportResult.watchlist_status || '').toUpperCase()}
                      size="small"
                      color={result.passportResult.watchlist_status === 'clear' ? 'success' : 'error'}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Audit Trail */}
          <Alert severity="info" icon={<Gavel />}>
            <Typography variant="subtitle2" fontWeight="bold">
              Audit Trail
            </Typography>
            <Typography variant="body2">
              Search ID: {result.searchId}
              <br />
              Audit ID: {result.auditTrailId}
              <br />
              Timestamp: {new Date(result.timestamp).toLocaleString()}
              <br />
              Officer: {result.officerId} | Case: {result.caseId}
            </Typography>
          </Alert>
        </Paper>
      )}

      {/* Search History */}
      {searchHistory.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <History sx={{ verticalAlign: 'middle', mr: 1 }} />
            Recent Searches (This Session)
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Search Type</TableCell>
                  <TableCell>Case ID</TableCell>
                  <TableCell>Match Score</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {searchHistory.slice(0, 10).map((search) => (
                  <TableRow key={search.searchId}>
                    <TableCell>{new Date(search.timestamp).toLocaleTimeString()}</TableCell>
                    <TableCell>
                      <Chip label={search.searchType.toUpperCase()} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{search.caseId}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${(search.matchScore * 100).toFixed(0)}%`}
                        size="small"
                        color={getMatchScoreColor(search.matchScore)}
                      />
                    </TableCell>
                    <TableCell>
                      {search.matchScore > 0.7 ? (
                        <CheckCircle color="success" fontSize="small" />
                      ) : (
                        <ErrorIcon color="error" fontSize="small" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  )
}
