"""
Real-time Security Monitoring Service

Integrates all security modules for continuous monitoring and alerting:
- Real-time log ingestion and processing
- Threat detection and analysis
- Automated response and alerting
- Dashboard integration
- Forensics data collection
"""

import asyncio
import aiohttp
from aiohttp import web
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any, Optional
import os
import signal
import threading
from queue import Queue, Empty
import time
from pathlib import Path

# Import our security modules
try:
    from features.security_features import SecurityFeatureExtractor
    from features.threat_detection import ComprehensiveThreatDetector
    from features.advanced_features import AdvancedFeatureExtractor
    from utils.security_ops import SecurityOperationsCenter
    SECURITY_MODULES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Security modules not available: {e}")
    SECURITY_MODULES_AVAILABLE = False

# Streaming and messaging
try:
    import asyncio_mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# Database and caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('security_monitoring.log')
    ]
)
logger = logging.getLogger(__name__)


class SecurityAlert:
    """Security alert data structure"""
    
    def __init__(self,
                 alert_id: str,
                 severity: str,
                 title: str,
                 description: str,
                 source_ip: Optional[str] = None,
                 affected_systems: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.alert_id = alert_id
        self.severity = severity  # critical, high, medium, low, info
        self.title = title
        self.description = description
        self.source_ip = source_ip
        self.affected_systems = affected_systems or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.status = 'open'  # open, investigating, resolved, false_positive
        self.assigned_to = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'source_ip': self.source_ip,
            'affected_systems': self.affected_systems,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'assigned_to': self.assigned_to
        }


class SecurityEventProcessor:
    """Process security events in real-time"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.event_queue = Queue(maxsize=10000)
        self.alert_queue = Queue(maxsize=1000)
        self.processing_stats = {
            'events_processed': 0,
            'alerts_generated': 0,
            'false_positives': 0,
            'start_time': datetime.now()
        }
        
        # Initialize security modules
        if SECURITY_MODULES_AVAILABLE:
            self.feature_extractor = SecurityFeatureExtractor()
            self.threat_detector = ComprehensiveThreatDetector()
            self.soc = SecurityOperationsCenter()
        else:
            logger.warning("Security modules not available - running in mock mode")
        
        # Initialize Redis for caching
        self.redis_client = None
        if REDIS_AVAILABLE and config.get('redis_url'):
            try:
                import redis
                self.redis_client = redis.from_url(config['redis_url'])
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
    
    def add_event(self, event_data: Dict[str, Any]) -> bool:
        """Add security event to processing queue"""
        try:
            self.event_queue.put(event_data, timeout=1)
            return True
        except:
            logger.warning("Event queue full - dropping event")
            return False
    
    async def process_events(self):
        """Main event processing loop"""
        logger.info("Starting security event processing...")
        
        while True:
            try:
                # Get events from queue
                events_batch = []
                while len(events_batch) < 100:  # Process in batches
                    try:
                        event = self.event_queue.get(timeout=0.1)
                        events_batch.append(event)
                        self.event_queue.task_done()
                    except Empty:
                        break
                
                if events_batch:
                    await self._process_event_batch(events_batch)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing events: {e}")
                await asyncio.sleep(1)
    
    async def _process_event_batch(self, events: List[Dict[str, Any]]):
        """Process a batch of security events"""
        try:
            # Convert to DataFrame for batch processing
            events_df = pd.DataFrame(events)
            
            if SECURITY_MODULES_AVAILABLE:
                # Extract security features
                features = await self._extract_features(events_df)
                
                # Run threat detection
                threats = await self._detect_threats(features, events_df)
                
                # Generate alerts for significant threats
                await self._generate_alerts(threats, events_df)
            else:
                # Mock processing for demonstration
                await self._mock_process_batch(events_df)
            
            self.processing_stats['events_processed'] += len(events)
            logger.info(f"Processed batch of {len(events)} events")
            
        except Exception as e:
            logger.error(f"Error processing event batch: {e}")
    
    async def _extract_features(self, events_df: pd.DataFrame) -> Dict[str, Any]:
        """Extract security features from events"""
        features = {}
        
        try:
            # Network analysis features
            if 'src_ip' in events_df.columns:
                network_features = self.feature_extractor.extract_network_features(events_df)
                features['network'] = network_features
            
            # Log analysis features
            if 'log_message' in events_df.columns:
                log_features = self.feature_extractor.extract_log_features(events_df)
                features['logs'] = log_features
            
            # Behavioral features
            behavioral_features = self.feature_extractor.extract_behavioral_features(events_df)
            features['behavioral'] = behavioral_features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            features = {'error': str(e)}
        
        return features
    
    async def _detect_threats(self, features: Dict[str, Any], events_df: pd.DataFrame) -> Dict[str, Any]:
        """Run threat detection analysis"""
        threats = {}
        
        try:
            # Anomaly detection
            anomalies = self.threat_detector.detect_anomalies(events_df)
            threats['anomalies'] = anomalies
            
            # Attack pattern detection
            attack_patterns = self.threat_detector.detect_attack_patterns(events_df)
            threats['attack_patterns'] = attack_patterns
            
            # C2 communication detection
            if 'network' in features:
                c2_detection = self.threat_detector.detect_c2_communication(events_df)
                threats['c2_communication'] = c2_detection
            
            # Data exfiltration detection
            exfiltration = self.threat_detector.detect_data_exfiltration(events_df)
            threats['data_exfiltration'] = exfiltration
            
        except Exception as e:
            logger.error(f"Threat detection error: {e}")
            threats = {'error': str(e)}
        
        return threats
    
    async def _generate_alerts(self, threats: Dict[str, Any], events_df: pd.DataFrame):
        """Generate security alerts based on threat detection results"""
        try:
            alert_count = 0
            
            # Anomaly alerts
            if threats.get('anomalies', {}).get('anomalies_detected', 0) > 0:
                alert = SecurityAlert(
                    alert_id=f"ANOM_{datetime.now().strftime('%Y%m%d%H%M%S')}_{alert_count}",
                    severity='medium',
                    title='Anomalous Behavior Detected',
                    description=f"Detected {threats['anomalies']['anomalies_detected']} anomalous events",
                    metadata={'anomaly_score': threats['anomalies'].get('anomaly_score', 0)}
                )
                self.alert_queue.put(alert)
                alert_count += 1
            
            # Attack pattern alerts
            if threats.get('attack_patterns', {}).get('total_attacks_detected', 0) > 0:
                attack_types = threats['attack_patterns'].get('attack_types', [])
                severity = 'high' if any('injection' in att.lower() for att in attack_types) else 'medium'
                
                alert = SecurityAlert(
                    alert_id=f"ATTACK_{datetime.now().strftime('%Y%m%d%H%M%S')}_{alert_count}",
                    severity=severity,
                    title='Attack Patterns Detected',
                    description=f"Detected attack patterns: {', '.join(attack_types)}",
                    metadata={'attack_details': threats['attack_patterns']}
                )
                self.alert_queue.put(alert)
                alert_count += 1
            
            # C2 communication alerts
            if threats.get('c2_communication', {}).get('beaconing_detected', False):
                alert = SecurityAlert(
                    alert_id=f"C2_{datetime.now().strftime('%Y%m%d%H%M%S')}_{alert_count}",
                    severity='critical',
                    title='Command and Control Communication Detected',
                    description='Suspicious beaconing behavior detected - possible C2 communication',
                    metadata={'c2_details': threats['c2_communication']}
                )
                self.alert_queue.put(alert)
                alert_count += 1
            
            # Data exfiltration alerts
            if threats.get('data_exfiltration', {}).get('exfiltration_detected', False):
                alert = SecurityAlert(
                    alert_id=f"EXFIL_{datetime.now().strftime('%Y%m%d%H%M%S')}_{alert_count}",
                    severity='critical',
                    title='Data Exfiltration Detected',
                    description='Suspicious data transfer patterns detected',
                    metadata={'exfiltration_details': threats['data_exfiltration']}
                )
                self.alert_queue.put(alert)
                alert_count += 1
            
            self.processing_stats['alerts_generated'] += alert_count
            
        except Exception as e:
            logger.error(f"Alert generation error: {e}")
    
    async def _mock_process_batch(self, events_df: pd.DataFrame):
        """Mock processing when security modules are not available"""
        # Generate mock alerts for demonstration
        if len(events_df) > 50:  # High volume might be suspicious
            alert = SecurityAlert(
                alert_id=f"MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                severity='medium',
                title='High Volume Activity',
                description=f'Detected {len(events_df)} events in batch',
                metadata={'event_count': len(events_df)}
            )
            self.alert_queue.put(alert)
            self.processing_stats['alerts_generated'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        runtime = datetime.now() - self.processing_stats['start_time']
        return {
            **self.processing_stats,
            'runtime_seconds': runtime.total_seconds(),
            'events_per_second': self.processing_stats['events_processed'] / max(runtime.total_seconds(), 1),
            'queue_size': self.event_queue.qsize(),
            'alert_queue_size': self.alert_queue.qsize()
        }


class SecurityAPI:
    """REST API for security monitoring service"""
    
    def __init__(self, event_processor: SecurityEventProcessor):
        self.event_processor = event_processor
        self.app = web.Application()
        self._setup_routes()
        self.connected_clients = set()  # For WebSocket clients
    
    def _setup_routes(self):
        """Setup API routes"""
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/stats', self.stats_handler)
        self.app.router.add_get('/alerts', self.alerts_handler)
        self.app.router.add_post('/events', self.events_handler)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Serve static files
        self.app.router.add_static('/', path='dashboard/', name='static')
    
    async def dashboard_handler(self, request):
        """Serve security dashboard"""
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Monitoring Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #1a1a1a; color: #fff; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .stat-card { background: #2d2d2d; padding: 20px; border-radius: 8px; border: 1px solid #444; }
                .stat-value { font-size: 2em; font-weight: bold; color: #4CAF50; }
                .stat-label { color: #aaa; margin-top: 5px; }
                .alerts-section { background: #2d2d2d; padding: 20px; border-radius: 8px; border: 1px solid #444; }
                .alert { padding: 15px; margin: 10px 0; border-left: 4px solid; border-radius: 4px; }
                .alert.critical { border-color: #f44336; background: rgba(244, 67, 54, 0.1); }
                .alert.high { border-color: #ff9800; background: rgba(255, 152, 0, 0.1); }
                .alert.medium { border-color: #ffeb3b; background: rgba(255, 235, 59, 0.1); }
                .alert.low { border-color: #4caf50; background: rgba(76, 175, 80, 0.1); }
                .refresh-btn { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                .refresh-btn:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Security Monitoring Dashboard</h1>
                    <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
                </div>
                
                <div class="stats-grid" id="stats-grid">
                    <!-- Stats will be loaded here -->
                </div>
                
                <div class="alerts-section">
                    <h2>Recent Alerts</h2>
                    <div id="alerts-container">
                        <!-- Alerts will be loaded here -->
                    </div>
                </div>
            </div>
            
            <script>
                async function loadStats() {
                    try {
                        const response = await fetch('/stats');
                        const stats = await response.json();
                        
                        document.getElementById('stats-grid').innerHTML = `
                            <div class="stat-card">
                                <div class="stat-value">${stats.events_processed}</div>
                                <div class="stat-label">Events Processed</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.alerts_generated}</div>
                                <div class="stat-label">Alerts Generated</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.events_per_second.toFixed(1)}</div>
                                <div class="stat-label">Events/Second</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.queue_size}</div>
                                <div class="stat-label">Queue Size</div>
                            </div>
                        `;
                    } catch (error) {
                        console.error('Error loading stats:', error);
                    }
                }
                
                async function loadAlerts() {
                    try {
                        const response = await fetch('/alerts');
                        const alerts = await response.json();
                        
                        const alertsHtml = alerts.map(alert => `
                            <div class="alert ${alert.severity}">
                                <strong>${alert.title}</strong> (${alert.severity.toUpperCase()})
                                <br>${alert.description}
                                <br><small>Time: ${new Date(alert.timestamp).toLocaleString()}</small>
                            </div>
                        `).join('');
                        
                        document.getElementById('alerts-container').innerHTML = alertsHtml || '<p>No recent alerts</p>';
                    } catch (error) {
                        console.error('Error loading alerts:', error);
                    }
                }
                
                function refreshData() {
                    loadStats();
                    loadAlerts();
                }
                
                // Load data on page load
                refreshData();
                
                // Refresh every 5 seconds
                setInterval(refreshData, 5000);
            </script>
        </body>
        </html>
        """
        return web.Response(text=dashboard_html, content_type='text/html')
    
    async def health_handler(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'security-monitoring'
        })
    
    async def stats_handler(self, request):
        """Return processing statistics"""
        stats = self.event_processor.get_stats()
        return web.json_response(stats)
    
    async def alerts_handler(self, request):
        """Return recent alerts"""
        alerts = []
        try:
            # Get up to 50 most recent alerts
            for _ in range(min(50, self.event_processor.alert_queue.qsize())):
                alert = self.event_processor.alert_queue.get_nowait()
                alerts.append(alert.to_dict())
                self.event_processor.alert_queue.put(alert)  # Put it back
        except Empty:
            pass
        
        # Sort by timestamp (most recent first)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        return web.json_response(alerts)
    
    async def events_handler(self, request):
        """Accept security events via HTTP POST"""
        try:
            event_data = await request.json()
            
            # Add timestamp if not present
            if 'timestamp' not in event_data:
                event_data['timestamp'] = datetime.now().isoformat()
            
            success = self.event_processor.add_event(event_data)
            
            if success:
                return web.json_response({'status': 'accepted', 'event_id': event_data.get('id', 'unknown')})
            else:
                return web.json_response({'status': 'rejected', 'reason': 'queue_full'}, status=503)
        
        except Exception as e:
            return web.json_response({'error': str(e)}, status=400)
    
    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        if not WEBSOCKETS_AVAILABLE:
            return web.Response(text='WebSockets not available', status=501)
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.connected_clients.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                        await ws.close()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        finally:
            self.connected_clients.discard(ws)
        
        return ws


class SecurityMonitoringService:
    """Main security monitoring service"""
    
    def __init__(self, config_path: str = 'config/security_config.yaml'):
        self.config = self._load_config(config_path)
        self.event_processor = SecurityEventProcessor(self.config)
        self.api = SecurityAPI(self.event_processor)
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration"""
        config = {
            'port': int(os.getenv('PORT', 8080)),
            'host': os.getenv('HOST', '0.0.0.0'),
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'max_events_per_second': int(os.getenv('MAX_EVENTS_PER_SECOND', 1000))
        }
        
        # Try to load from file
        config_file = Path(config_path)
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    config.update(file_config)
            except ImportError:
                logger.warning("PyYAML not available - using environment config only")
            except Exception as e:
                logger.warning(f"Error loading config file: {e}")
        
        return config
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start(self):
        """Start the security monitoring service"""
        logger.info("Starting Security Monitoring Service...")
        
        self.running = True
        
        # Start event processing task
        event_task = asyncio.create_task(self.event_processor.process_events())
        
        # Start web server
        runner = web.AppRunner(self.api.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.config['host'], self.config['port'])
        await site.start()
        
        logger.info(f"Security Monitoring Service started on http://{self.config['host']}:{self.config['port']}")
        logger.info("Dashboard available at: http://localhost:{}/".format(self.config['port']))
        
        # Keep the service running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            logger.info("Shutting down...")
            event_task.cancel()
            await runner.cleanup()
    
    def generate_sample_events(self, count: int = 100):
        """Generate sample security events for testing"""
        import random
        from datetime import datetime, timedelta
        
        sample_ips = ['192.168.1.100', '10.0.0.5', '172.16.0.10', '203.0.113.1', '198.51.100.1']
        sample_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'curl/7.68.0',
            'Malicious Scanner v1.0',
            'sqlmap/1.4.7',
            'nikto/2.1.6'
        ]
        sample_urls = ['/login', '/admin', '/api/users', '/../../../etc/passwd', '/wp-admin', '/dashboard']
        
        events = []
        base_time = datetime.now() - timedelta(minutes=30)
        
        for i in range(count):
            event = {
                'id': f'event_{i:06d}',
                'timestamp': (base_time + timedelta(seconds=i*2)).isoformat(),
                'src_ip': random.choice(sample_ips),
                'dst_port': random.choice([80, 443, 22, 21, 3389]),
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'url': random.choice(sample_urls),
                'user_agent': random.choice(sample_user_agents),
                'status_code': random.choice([200, 401, 403, 404, 500]),
                'response_size': random.randint(100, 10000),
                'event_type': 'web_request'
            }
            
            # Add some suspicious patterns
            if i % 20 == 0:  # Every 20th event is suspicious
                event['url'] = random.choice(['/../../../etc/passwd', '/admin', '/../../../windows/system32'])
                event['user_agent'] = 'Malicious Scanner v1.0'
                event['status_code'] = 404
            
            events.append(event)
        
        # Add events to processor
        for event in events:
            self.event_processor.add_event(event)
        
        logger.info(f"Generated {count} sample security events")


async def main():
    """Main entry point"""
    service = SecurityMonitoringService()
    
    # Generate some sample events for demonstration
    service.generate_sample_events(200)
    
    # Start the service
    await service.start()


if __name__ == '__main__':
    asyncio.run(main())