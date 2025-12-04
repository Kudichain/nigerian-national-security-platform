import { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Search as SearchIcon,
  Description as DescriptionIcon,
  Flight as FlightIcon,
  Security as SecurityIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { verifyVisa, type VisaVerificationResult } from '../api/securityApi';

export default function VisaVerification() {
  const [visaNumber, setVisaNumber] = useState('');
  const [passportNumber, setPassportNumber] = useState('');
  const [country, setCountry] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VisaVerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    if (!visaNumber.trim() || !passportNumber.trim()) {
      setError('Please enter both visa number and passport number');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const response = await verifyVisa({
      visaNumber: visaNumber.trim(),
      passportNumber: passportNumber.trim(),
      country: country.trim() || undefined,
    });

    setLoading(false);

    if (response.error) {
      setError(response.error);
    } else if (response.data) {
      setResult(response.data);
    }
  };

  const handleClear = () => {
    setVisaNumber('');
    setPassportNumber('');
    setCountry('');
    setResult(null);
    setError(null);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid':
        return 'success';
      case 'expired':
        return 'warning';
      case 'cancelled':
      case 'restricted':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          <SecurityIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Visa Verification System
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time visa verification and status checking for immigration control
        </Typography>
      </Box>

      {/* Verification Form */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Enter Verification Details
        </Typography>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Visa Number"
              value={visaNumber}
              onChange={(e) => setVisaNumber(e.target.value)}
              placeholder="e.g., V123456789"
              disabled={loading}
              onKeyPress={(e) => e.key === 'Enter' && handleVerify()}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Passport Number"
              value={passportNumber}
              onChange={(e) => setPassportNumber(e.target.value)}
              placeholder="e.g., AB1234567"
              disabled={loading}
              onKeyPress={(e) => e.key === 'Enter' && handleVerify()}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Country (Optional)"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              placeholder="e.g., USA"
              disabled={loading}
              onKeyPress={(e) => e.key === 'Enter' && handleVerify()}
            />
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                onClick={handleVerify}
                disabled={loading}
                size="large"
              >
                {loading ? 'Verifying...' : 'Verify Visa'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleClear}
                disabled={loading}
                size="large"
              >
                Clear
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Verification Result */}
      {result && (
        <>
          {/* Status Banner */}
          <Alert
            severity={result.valid ? 'success' : 'error'}
            icon={result.valid ? <CheckCircleIcon /> : <ErrorIcon />}
            sx={{ mb: 3 }}
          >
            <Typography variant="h6">
              {result.status === 'not_found'
                ? 'Visa Not Found'
                : result.valid
                ? 'Valid Visa Confirmed'
                : 'Invalid Visa Detected'}
            </Typography>
            <Typography variant="body2">
              {result.message || `Verification completed at ${new Date(result.timestamp).toLocaleString()}`}
            </Typography>
          </Alert>

          {/* Visa Details */}
          {result.visa_details && (
            <Grid container spacing={3}>
              {/* Main Details Card */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Visa Details
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary="Visa Number"
                          secondary={result.visa_number}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Passport Number"
                          secondary={result.passport_number}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Visa Type"
                          secondary={
                            <Chip
                              label={result.visa_details.visa_type.toUpperCase()}
                              size="small"
                              color="primary"
                            />
                          }
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Status"
                          secondary={
                            <Chip
                              label={result.visa_details.status.toUpperCase()}
                              size="small"
                              color={getStatusColor(result.visa_details.status)}
                            />
                          }
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Country of Issue"
                          secondary={result.visa_details.country_of_issue}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              {/* Dates and Usage Card */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <TimerIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Validity & Usage
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary="Issue Date"
                          secondary={new Date(result.visa_details.issue_date).toLocaleDateString()}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Expiry Date"
                          secondary={new Date(result.visa_details.expiry_date).toLocaleDateString()}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Entries Allowed"
                          secondary={result.visa_details.entries_allowed}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Entries Used"
                          secondary={result.visa_details.entries_used}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Duration of Stay"
                          secondary={`${result.visa_details.duration_of_stay_days} days`}
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>

              {/* Warnings Card */}
              {result.warnings && result.warnings.filter(Boolean).length > 0 && (
                <Grid item xs={12}>
                  <Alert severity="warning" icon={<WarningIcon />}>
                    <Typography variant="subtitle2" gutterBottom>
                      Warnings
                    </Typography>
                    <List dense>
                      {result.warnings.filter(Boolean).map((warning, idx) => (
                        <ListItem key={idx} sx={{ pl: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <WarningIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={warning} />
                        </ListItem>
                      ))}
                    </List>
                  </Alert>
                </Grid>
              )}

              {/* Restrictions Card */}
              {result.restrictions && result.restrictions.filter(Boolean).length > 0 && (
                <Grid item xs={12}>
                  <Alert severity="info">
                    <Typography variant="subtitle2" gutterBottom>
                      Restrictions
                    </Typography>
                    <List dense>
                      {result.restrictions.filter(Boolean).map((restriction, idx) => (
                        <ListItem key={idx} sx={{ pl: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <FlightIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={restriction} />
                        </ListItem>
                      ))}
                    </List>
                  </Alert>
                </Grid>
              )}

              {/* Verification Metadata */}
              {result.verification_details && (
                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Verification Metadata
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Method
                          </Typography>
                          <Typography variant="body1">
                            {result.verification_details.verification_method}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Confidence Score
                          </Typography>
                          <Typography variant="body1">
                            {(result.verification_details.confidence_score * 100).toFixed(1)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Verified At
                          </Typography>
                          <Typography variant="body1">
                            {new Date(result.verification_details.verified_at).toLocaleString()}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          )}
        </>
      )}
    </Container>
  );
}
