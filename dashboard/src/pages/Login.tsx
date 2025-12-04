import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Container,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Tabs,
  Tab,
} from '@mui/material'
import { Fingerprint, CheckCircle, ErrorOutline, Login as LoginIcon } from '@mui/icons-material'
import { useAuthStore } from '../store/authStore'

// Backend API configuration
const BIOMETRIC_API_URL = 'http://localhost:8000/api/v1/biometric'

interface CredentialDescriptorResponse {
  id: string
  type: PublicKeyCredentialType
  transports?: AuthenticatorTransport[]
}

interface AuthenticationOptionsResponse {
  challenge: string
  challenge_id: string
  timeout: number
  userVerification: UserVerificationRequirement
  rpId?: string
  allowCredentials?: CredentialDescriptorResponse[]
}

interface RegistrationOptionsResponse {
  challenge: string
  challenge_id: string
  timeout: number
  rp: {
    name: string
    id: string
  }
  user: {
    id: string
    name: string
    displayName: string
  }
  pubKeyCredParams: PublicKeyCredentialParameters[]
  attestation: AttestationConveyancePreference
}

export default function Login() {
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [scanning, setScanning] = useState(false)
  const [biometricAvailable, setBiometricAvailable] = useState<boolean | null>(null)
  const [enrollmentMode, setEnrollmentMode] = useState(false)
  const [authStep, setAuthStep] = useState(0)
  const [authTab, setAuthTab] = useState(0) // 0 = Token, 1 = Biometric
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const { login } = useAuthStore()

  useEffect(() => {
    checkBiometricSupport()
    checkBackendHealth()
  }, [])

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/biometric/health', {
        method: 'GET',
        mode: 'cors',
      })
      if (response.ok) {
        const data = await response.json()
        console.log('✅ Backend connected:', data)
        return true
      } else {
        console.error('❌ Backend returned error:', response.status)
        setError('Backend service not responding. Please ensure port 8000 is running.')
        return false
      }
    } catch (err) {
      console.error('❌ Backend connection failed:', err)
      setError('Cannot connect to biometric service. Please start the main API server on port 8000')
      return false
    }
  }

  const checkBiometricSupport = async () => {
    if (!window.PublicKeyCredential) {
      setBiometricAvailable(false)
      setError('WebAuthn not supported. Please use a modern browser with biometric support.')
      return false
    }
    
    try {
      const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
      setBiometricAvailable(available)
      
      if (!available) {
        setError('No biometric device detected. Please enable Windows Hello, Touch ID, or connect a fingerprint reader.')
      } else {
        setSuccess('✓ Biometric authentication ready')
      }
      return available
    } catch (err) {
      console.error('Biometric check failed:', err)
      setBiometricAvailable(false)
      setError('Unable to access biometric hardware')
      return false
    }
  }

  const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return window.btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
  }

  const base64ToArrayBuffer = (base64: string): ArrayBuffer => {
    // Add padding if needed
    const padding = '='.repeat((4 - base64.length % 4) % 4)
    const b64 = base64.replace(/-/g, '+').replace(/_/g, '/') + padding
    const binary = window.atob(b64)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i)
    }
    return bytes.buffer
  }

  const enrollBiometric = async () => {
    setError('')
    setSuccess('')
    setScanning(true)
    setAuthStep(1)

    try {
      // Step 0: Check backend health
      const backendOk = await checkBackendHealth()
      if (!backendOk) {
        setScanning(false)
        setAuthStep(0)
        return
      }

      // Step 1: Get registration options from backend
      setSuccess('Requesting registration options from server...')
      const optionsResponse = await fetch(`${BIOMETRIC_API_URL}/register/options`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        body: JSON.stringify({
          username: 'security-admin',
          display_name: 'Security Administrator'
        })
      })

      if (!optionsResponse.ok) {
        const errorData = await optionsResponse.json().catch(() => ({ detail: 'Server error' }))
        throw new Error(errorData.detail || `HTTP ${optionsResponse.status}`)
      }

      const options: RegistrationOptionsResponse = await optionsResponse.json()
      
      // Step 2: Create credential with actual biometric scan
      setAuthStep(2)
      setSuccess('👆 Place your finger on the sensor and hold...')

      // Convert base64url to ArrayBuffer
      const userId = base64ToArrayBuffer(options.user.id)
      const challenge = base64ToArrayBuffer(options.challenge)
      const challengeId = options.challenge_id
      
      const publicKeyCredentialCreationOptions: PublicKeyCredentialCreationOptions = {
        challenge,
        rp: {
          name: options.rp.name,
          id: options.rp.id,
        },
        user: {
          id: userId,
          name: options.user.name,
          displayName: options.user.displayName,
        },
        pubKeyCredParams: options.pubKeyCredParams,
        authenticatorSelection: {
          authenticatorAttachment: 'platform' as AuthenticatorAttachment,
          userVerification: 'required' as UserVerificationRequirement,
          requireResidentKey: true,
          residentKey: 'required' as ResidentKeyRequirement,
        },
        timeout: options.timeout,
        attestation: options.attestation as AttestationConveyancePreference,
      }

      const credential = await navigator.credentials.create({
        publicKey: publicKeyCredentialCreationOptions,
      }) as PublicKeyCredential

      if (credential && credential.rawId) {
        setAuthStep(3)
        setSuccess('🔐 Verifying biometric signature with backend...')
        
        // Step 3: Send credential to backend for verification
        const response = credential.response as AuthenticatorAttestationResponse
        
        const verifyResponse = await fetch(`${BIOMETRIC_API_URL}/register/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            credential_id: arrayBufferToBase64(credential.rawId),
            client_data_json: arrayBufferToBase64(response.clientDataJSON),
            attestation_object: arrayBufferToBase64(response.attestationObject),
            user_id: options.user.id,
            challenge_id: challengeId
          })
        })

        if (!verifyResponse.ok) {
          const errorData = await verifyResponse.json()
          throw new Error(errorData.detail || 'Verification failed')
        }

        const verifyData = await verifyResponse.json()
        
        // Store session token
        localStorage.setItem('biometric_session_token', verifyData.session_token)
        localStorage.setItem('biometric_user_id', verifyData.user_id)
        localStorage.setItem('biometric_username', verifyData.username)
        localStorage.setItem('biometric_enrolled', 'true')

        setSuccess('✓ Fingerprint enrolled and verified!')
        setAuthStep(4)
        
        // Login with backend session
        setTimeout(async () => {
          await login(verifyData.username, verifyData.username)
        }, 1000)
      }
    } catch (error: unknown) {
      console.error('Enrollment error:', error)
      setAuthStep(0)
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          setError('Fingerprint scan cancelled. Please try again.')
        } else if (error.name === 'InvalidStateError') {
          setError('Biometric already enrolled. Use authentication instead.')
          setEnrollmentMode(false)
        } else if (error.name === 'NotSupportedError') {
          setError('Your device does not support this biometric method.')
        } else {
          setError(`Enrollment failed: ${error.message || 'Unknown error'}`)
        }
      } else {
        setError('Enrollment failed: Unknown error')
      }
    } finally {
      setScanning(false)
    }
  }

  const authenticateWithBiometric = async () => {
    setError('')
    setSuccess('')
    setScanning(true)
    setAuthStep(1)

    try {
      // Step 0: Check backend health
      const backendOk = await checkBackendHealth()
      if (!backendOk) {
        setScanning(false)
        setAuthStep(0)
        return
      }

      // Step 1: Get authentication options from backend
      setSuccess('Requesting authentication challenge...')
      const optionsResponse = await fetch(`${BIOMETRIC_API_URL}/authenticate/options`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        body: JSON.stringify({
          username: localStorage.getItem('biometric_username') || 'security-admin'
        })
      })

      if (!optionsResponse.ok) {
        const errorData = await optionsResponse.json().catch(() => ({ detail: 'Server error' }))
        throw new Error(errorData.detail || `HTTP ${optionsResponse.status}`)
      }

      const options: AuthenticationOptionsResponse = await optionsResponse.json()
      
      // Step 2: Get assertion with biometric
      setAuthStep(2)
      setSuccess('👆 Scan your fingerprint to authenticate...')

      const challenge = base64ToArrayBuffer(options.challenge)
      const challengeId = options.challenge_id
      const allowCredentials = options.allowCredentials?.map((cred) => ({
        id: base64ToArrayBuffer(cred.id),
        type: cred.type,
        transports: cred.transports,
      }))

      const publicKeyCredentialRequestOptions: PublicKeyCredentialRequestOptions = {
        challenge,
        timeout: options.timeout,
        userVerification: options.userVerification as UserVerificationRequirement,
        rpId: options.rpId,
        allowCredentials: allowCredentials && allowCredentials.length > 0 ? allowCredentials : undefined,
      }

      const assertion = await navigator.credentials.get({
        publicKey: publicKeyCredentialRequestOptions,
      }) as PublicKeyCredential

      if (assertion) {
        setAuthStep(3)
        setSuccess('🔐 Verifying with backend...')
        
        // Step 3: Verify assertion with backend
        const response = assertion.response as AuthenticatorAssertionResponse
        
        const verifyResponse = await fetch(`${BIOMETRIC_API_URL}/authenticate/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            credential_id: arrayBufferToBase64(assertion.rawId),
            client_data_json: arrayBufferToBase64(response.clientDataJSON),
            authenticator_data: arrayBufferToBase64(response.authenticatorData),
            signature: arrayBufferToBase64(response.signature),
            user_handle: response.userHandle ? arrayBufferToBase64(response.userHandle) : null,
            challenge_id: challengeId
          })
        })

        if (!verifyResponse.ok) {
          const errorData = await verifyResponse.json()
          throw new Error(errorData.detail || 'Authentication failed')
        }

        const verifyData = await verifyResponse.json()
        
        // Store session
        localStorage.setItem('biometric_session_token', verifyData.session_token)
        localStorage.setItem('biometric_user_id', verifyData.user_id)
        localStorage.setItem('biometric_username', verifyData.username)

        setSuccess('✓ Fingerprint verified!')
        setAuthStep(4)
        
        // Login
        setTimeout(async () => {
          await login(verifyData.username, verifyData.username)
        }, 800)
      }
    } catch (error: unknown) {
      console.error('Authentication error:', error)
      setAuthStep(0)
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          setError('Fingerprint authentication cancelled or failed. Please try again.')
        } else if (error.name === 'InvalidStateError') {
          setError('No biometric enrolled. Please enroll your fingerprint first.')
          setEnrollmentMode(true)
        } else if (error.name === 'NotSupportedError') {
          setError('Biometric authentication not supported on this device.')
        } else {
          setError(`Authentication failed: ${error.message || 'Please try again'}`)
        }
      } else {
        setError('Authentication failed: Please try again')
      }
    } finally {
      setScanning(false)
    }
  }

  const handleBiometricFlow = async () => {
    if (!biometricAvailable) {
      await checkBiometricSupport()
      return
    }

    // Check if already enrolled
    const enrolled = localStorage.getItem('biometric_enrolled')
    
    if (enrollmentMode || !enrolled) {
      await enrollBiometric()
    } else {
      await authenticateWithBiometric()
    }
  }

  const handleTokenLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoginLoading(true)

    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password')
      setLoginLoading(false)
      return
    }

    try {
      // Mock token authentication
      const mockToken = `token_${username}_${Date.now()}`

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Store token and login
      localStorage.setItem('authToken', mockToken)
      localStorage.setItem('user', JSON.stringify({ username, role: 'admin' }))
      
      setSuccess(`✓ Welcome, ${username}!`)
      login(username, password)
      
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } catch (err) {
      setError('Authentication failed. Please try again.')
    } finally {
      setLoginLoading(false)
    }
  }

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setAuthTab(newValue)
    setError('')
    setSuccess('')
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Card sx={{ mt: 3, width: '100%' }}>
          <CardContent sx={{ p: 4 }}>
            <Typography component="h1" variant="h4" align="center" gutterBottom>
              🛡️ Security AI
            </Typography>
            <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
              National Security Platform
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {success}
              </Alert>
            )}

            {/* Authentication Tabs */}
            <Tabs 
              value={authTab} 
              onChange={handleTabChange} 
              variant="fullWidth"
              sx={{ mb: 3 }}
            >
              <Tab label="Token Login" icon={<LoginIcon />} iconPosition="start" />
              <Tab label="Biometric" icon={<Fingerprint />} iconPosition="start" />
            </Tabs>

            {/* Tab 0: Token Authentication */}
            {authTab === 0 && (
              <Box component="form" onSubmit={handleTokenLogin} sx={{ mt: 3 }}>
                <TextField
                  fullWidth
                  label="Username"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  margin="normal"
                  disabled={loginLoading}
                  autoComplete="username"
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  margin="normal"
                  disabled={loginLoading}
                  autoComplete="current-password"
                />
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  type="submit"
                  disabled={loginLoading || !username || !password}
                  startIcon={loginLoading ? <CircularProgress size={20} /> : <LoginIcon />}
                  sx={{ mt: 3 }}
                >
                  {loginLoading ? 'Authenticating...' : 'Sign In'}
                </Button>
                <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 2 }}>
                  🔐 Demo credentials: admin / password123
                </Typography>
              </Box>
            )}

            {/* Tab 1: Biometric Authentication */}
            {authTab === 1 && (
              <>
                {scanning && (
                  <Box sx={{ width: '100%', mb: 3 }}>
                    <Stepper activeStep={authStep} alternativeLabel>
                      <Step>
                        <StepLabel>Initialize</StepLabel>
                      </Step>
                      <Step>
                        <StepLabel>Scan Fingerprint</StepLabel>
                      </Step>
                      <Step>
                        <StepLabel>Verify</StepLabel>
                      </Step>
                      <Step>
                        <StepLabel>Complete</StepLabel>
                      </Step>
                    </Stepper>
                  </Box>
                )}

                <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <Box
                    sx={{
                      width: 140,
                      height: 140,
                      borderRadius: '50%',
                      border: '4px solid',
                      borderColor: scanning 
                        ? 'success.main' 
                        : biometricAvailable 
                        ? 'primary.main' 
                        : 'error.main',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 3,
                      bgcolor: scanning 
                        ? 'success.dark' 
                        : biometricAvailable === false 
                        ? 'error.dark' 
                        : 'primary.dark',
                      transition: 'all 0.3s ease',
                      cursor: biometricAvailable ? 'pointer' : 'not-allowed',
                      animation: scanning ? 'pulse 2s infinite' : 'none',
                      '@keyframes pulse': {
                        '0%': { transform: 'scale(1)', opacity: 1 },
                        '50%': { transform: 'scale(1.05)', opacity: 0.8 },
                        '100%': { transform: 'scale(1)', opacity: 1 },
                      },
                      '&:hover': biometricAvailable ? {
                        borderColor: 'success.main',
                        bgcolor: 'success.dark',
                        transform: 'scale(1.05)',
                      } : {},
                    }}
                    onClick={biometricAvailable ? handleBiometricFlow : undefined}
                  >
                    {scanning ? (
                      <CircularProgress size={70} thickness={2} sx={{ color: 'success.light' }} />
                    ) : biometricAvailable === false ? (
                      <ErrorOutline sx={{ fontSize: 90, color: 'error.light' }} />
                    ) : authStep === 4 ? (
                      <CheckCircle sx={{ fontSize: 90, color: 'success.light' }} />
                    ) : (
                      <Fingerprint sx={{ fontSize: 90, color: 'primary.light' }} />
                    )}
                  </Box>

                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handleBiometricFlow}
                    disabled={scanning || biometricAvailable === false}
                    startIcon={scanning ? <CircularProgress size={20} /> : <Fingerprint />}
                    sx={{ 
                      mt: 1, 
                      mb: 2,
                      bgcolor: enrollmentMode ? 'warning.main' : 'primary.main',
                      '&:hover': {
                        bgcolor: enrollmentMode ? 'warning.dark' : 'primary.dark',
                      },
                    }}
                  >
                    {scanning 
                      ? 'Scanning Fingerprint...' 
                      : enrollmentMode 
                      ? 'Enroll Fingerprint' 
                      : 'Authenticate with Fingerprint'}
                  </Button>

                  {!enrollmentMode && biometricAvailable && (
                    <Button
                      variant="text"
                      size="small"
                      onClick={() => setEnrollmentMode(true)}
                      sx={{ mb: 1 }}
                    >
                      Re-enroll Fingerprint
                    </Button>
                  )}

                  <Typography 
                    variant="caption" 
                    color="text.secondary" 
                    align="center" 
                    display="block"
                    sx={{ mt: 1 }}
                  >
                    {scanning 
                      ? authStep === 2 
                        ? '👆 Place and hold your finger on the sensor' 
                        : authStep === 3 
                        ? '🔐 Verifying biometric signature with server...' 
                        : '⏳ Preparing secure authentication...'
                      : biometricAvailable === false
                      ? '⚠️ Biometric hardware not available'
                      : enrollmentMode
                      ? '📝 First-time setup: Register your fingerprint'
                      : '🔒 Secure biometric authentication enabled'}
                  </Typography>

                  {biometricAvailable && (
                    <Typography 
                      variant="caption" 
                      color="success.main" 
                      align="center" 
                      display="block"
                      sx={{ mt: 1, fontWeight: 'bold' }}
                    >
                      ✓ WebAuthn Level 2 | Hardware Security Module Active
                    </Typography>
                  )}
                </Box>
              </>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}
