import { useEffect, useRef } from 'react'
import Hls from 'hls.js'
import { Box, Typography, Alert } from '@mui/material'
import { Videocam } from '@mui/icons-material'

interface VideoPlayerProps {
  streamUrl?: string
  rtcOfferUrl?: string
  className?: string
  title?: string
}

export default function VideoPlayer({ streamUrl, rtcOfferUrl, className, title }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const hlsRef = useRef<Hls | null>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video || !streamUrl) return

    // Cleanup previous HLS instance
    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }

    // Prefer WebRTC if rtcOfferUrl provided (placeholder for future implementation)
    if (rtcOfferUrl) {
      // TODO: Implement WebRTC signaling and connection
      console.log('WebRTC connection to:', rtcOfferUrl)
    }

    // HLS playback
    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90,
      })
      
      hlsRef.current = hls
      hls.loadSource(streamUrl)
      hls.attachMedia(video)
      
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch((error) => {
          console.warn('Autoplay prevented:', error)
        })
      })

      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.error('Network error, attempting recovery...')
              hls.startLoad()
              break
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.error('Media error, attempting recovery...')
              hls.recoverMediaError()
              break
            default:
              console.error('Fatal error, cannot recover')
              hls.destroy()
              break
          }
        }
      })

      return () => {
        hls.destroy()
        hlsRef.current = null
      }
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      video.src = streamUrl
      video.addEventListener('loadedmetadata', () => {
        video.play().catch((error) => {
          console.warn('Autoplay prevented:', error)
        })
      })
    }

    return () => {
      if (video) {
        video.pause()
        video.src = ''
      }
    }
  }, [streamUrl, rtcOfferUrl])

  if (!streamUrl) {
    return (
      <Box
        className={className}
        sx={{
          width: '100%',
          height: '100%',
          minHeight: 400,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
          borderRadius: 2,
          border: '2px dashed rgba(255,255,255,0.1)',
        }}
      >
        <Videocam sx={{ fontSize: 64, color: 'rgba(255,255,255,0.3)', mb: 2 }} />
        <Typography variant="h6" color="rgba(255,255,255,0.5)">
          No stream selected
        </Typography>
        <Typography variant="body2" color="rgba(255,255,255,0.3)" sx={{ mt: 1 }}>
          Select a camera or drone to view live feed
        </Typography>
      </Box>
    )
  }

  return (
    <Box className={className} sx={{ width: '100%', height: '100%' }}>
      {title && (
        <Box sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Videocam color="error" />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            🔴 LIVE: {title}
          </Typography>
        </Box>
      )}
      
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          paddingTop: '56.25%', // 16:9 aspect ratio
          background: '#000',
          borderRadius: 2,
          overflow: 'hidden',
          border: '2px solid rgba(244, 67, 54, 0.5)',
          boxShadow: '0 0 20px rgba(244, 67, 54, 0.3)',
        }}
      >
        <Box
          component="video"
          ref={videoRef}
          controls
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'contain',
          }}
        />
      </Box>

      {!Hls.isSupported() && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Your browser does not support HLS playback. Please use a modern browser.
        </Alert>
      )}
    </Box>
  )
}
