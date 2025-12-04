"""
Edge AI Processing for Drone Surveillance
Privacy-first biometric template extraction with local filtering
"""
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import numpy as np
import cv2
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DeviceAttestation:
    """Hardware-backed device identity"""
    device_id: str
    public_key: bytes
    manufacturer: str
    firmware_version: str
    attestation_cert: Optional[bytes] = None
    
    def sign_data(self, private_key: rsa.RSAPrivateKey, data: bytes) -> bytes:
        """Sign data with device private key"""
        return private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )


@dataclass
class BiometricTemplate:
    """Privacy-preserving face embedding (not raw image)"""
    template_hash: str  # SHA256 of embedding
    embedding: np.ndarray  # 128-d face descriptor
    confidence: float
    metadata: Dict[str, Any]
    
    def encrypt(self, encryption_key: bytes) -> bytes:
        """Encrypt template for transmission"""
        fernet = Fernet(encryption_key)
        template_bytes = json.dumps({
            'template_hash': self.template_hash,
            'embedding': self.embedding.tolist(),
            'confidence': self.confidence,
            'metadata': self.metadata
        }).encode()
        return fernet.encrypt(template_bytes)
    
    def to_pseudonymous_token(self, salt: str) -> str:
        """Generate one-way token (for tokenized matching)"""
        token_input = f"{self.template_hash}:{salt}".encode()
        return hashlib.sha256(token_input).hexdigest()


class PrivacyFilter:
    """Local privacy enforcement on edge device"""
    
    def __init__(self, video_ttl_seconds: int = 30, blur_non_targets: bool = True):
        self.video_ttl = timedelta(seconds=video_ttl_seconds)
        self.blur_non_targets = blur_non_targets
        self.created_videos: Dict[str, datetime] = {}
    
    def blur_faces(self, frame: np.ndarray, face_boxes: List[tuple]) -> np.ndarray:
        """Blur detected faces for privacy"""
        blurred = frame.copy()
        for (x, y, w, h) in face_boxes:
            roi = blurred[y:y+h, x:x+w]
            blurred[y:y+h, x:x+w] = cv2.GaussianBlur(roi, (51, 51), 30)
        return blurred
    
    def enforce_ttl(self, video_path: str, created_time: datetime):
        """Delete video after TTL expires"""
        if datetime.now() - created_time > self.video_ttl:
            try:
                import os
                if os.path.exists(video_path):
                    os.remove(video_path)
                    logger.info(f"Deleted expired video: {video_path}")
            except Exception as e:
                logger.error(f"Failed to delete {video_path}: {e}")
    
    def add_differential_noise(self, embedding: np.ndarray, epsilon: float = 0.1) -> np.ndarray:
        """Add Laplace noise for differential privacy (optional)"""
        sensitivity = 2.0  # L2 sensitivity of embeddings
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale, embedding.shape)
        return embedding + noise


class FaceDetector:
    """Face detection and embedding extraction"""
    
    def __init__(self, model_path: str = "models/face_detection.pb"):
        # In production, load actual DNN model (e.g., dlib, FaceNet, ArcFace)
        # For demo, we simulate
        self.model_loaded = True
        logger.info("Face detector initialized")
    
    def detect_faces(self, frame: np.ndarray) -> List[tuple]:
        """Detect faces and return bounding boxes"""
        # Simulated detection - replace with actual model
        # E.g., using cv2.dnn.readNetFromTensorflow or dlib
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        return [(x, y, w, h) for (x, y, w, h) in faces]
    
    def extract_embedding(self, frame: np.ndarray, face_box: tuple) -> np.ndarray:
        """Extract 128-d face embedding from face region"""
        # Simulated embedding - replace with actual FaceNet/ArcFace
        x, y, w, h = face_box
        face_roi = frame[y:y+h, x:x+w]
        
        # Placeholder: generate deterministic embedding from face pixels
        # In production: use pre-trained FaceNet, ArcFace, or DeepFace
        face_resized = cv2.resize(face_roi, (128, 128))
        embedding = face_resized.flatten()[:128].astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        return embedding


class DroneEdgeProcessor:
    """Main edge processing pipeline for drone surveillance"""
    
    def __init__(
        self,
        device_id: str,
        encryption_key: bytes,
        private_key: rsa.RSAPrivateKey,
        video_ttl: int = 30,
        enable_differential_privacy: bool = False
    ):
        self.device_id = device_id
        self.encryption_key = encryption_key
        self.private_key = private_key
        self.public_key = private_key.public_key()
        
        self.attestation = DeviceAttestation(
            device_id=device_id,
            public_key=self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ),
            manufacturer="SecureEdge Corp",
            firmware_version="v2.1.3"
        )
        
        self.privacy_filter = PrivacyFilter(video_ttl_seconds=video_ttl)
        self.face_detector = FaceDetector()
        self.enable_dp = enable_differential_privacy
        
        logger.info(f"Drone edge processor initialized: {device_id}")
    
    def process_frame(
        self,
        frame: np.ndarray,
        location: Dict[str, float],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Process video frame and return encrypted templates
        
        Returns list of detection events with encrypted templates
        """
        # Step 1: Detect faces
        face_boxes = self.face_detector.detect_faces(frame)
        
        if not face_boxes:
            return []
        
        # Step 2: Blur non-target faces if enabled
        if self.privacy_filter.blur_non_targets:
            frame = self.privacy_filter.blur_faces(frame, face_boxes)
        
        # Step 3: Extract embeddings and create templates
        templates = []
        for face_box in face_boxes:
            # Extract embedding
            embedding = self.face_detector.extract_embedding(frame, face_box)
            
            # Apply differential privacy noise if enabled
            if self.enable_dp:
                embedding = self.privacy_filter.add_differential_noise(embedding, epsilon=0.1)
            
            # Create template hash
            template_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
            
            # Create biometric template (NO RAW IMAGE)
            template = BiometricTemplate(
                template_hash=template_hash,
                embedding=embedding,
                confidence=0.85,  # Placeholder - would come from model
                metadata={
                    'bbox': face_box,
                    'location': location,
                    'timestamp': datetime.utcnow().isoformat(),
                    'device_id': self.device_id,
                    **metadata
                }
            )
            
            # Encrypt template
            encrypted_template = template.encrypt(self.encryption_key)
            
            # Sign the payload
            signature = self.attestation.sign_data(
                self.private_key,
                encrypted_template
            )
            
            templates.append({
                'device_id': self.device_id,
                'timestamp': template.metadata['timestamp'],
                'location': location,
                'template': encrypted_template.decode('utf-8'),
                'signature': signature.hex(),
                'confidence': template.confidence,
                'metadata': {
                    'camera_height_m': metadata.get('altitude', 120),
                    'weather': metadata.get('weather', 'unknown')
                }
            })
        
        return templates
    
    def create_match_request(
        self,
        frame: np.ndarray,
        location: Dict[str, float],
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create API request payload for identity matching
        Returns None if no faces detected
        """
        templates = self.process_frame(frame, location, metadata)
        
        if not templates:
            return None
        
        # Return first template (or batch all)
        return templates[0]


def generate_device_keypair() -> tuple[rsa.RSAPrivateKey, bytes]:
    """Generate device attestation keypair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key, public_pem


# Example usage
if __name__ == "__main__":
    # Initialize device
    private_key, public_key = generate_device_keypair()
    encryption_key = Fernet.generate_key()
    
    processor = DroneEdgeProcessor(
        device_id="drone-abc-123",
        encryption_key=encryption_key,
        private_key=private_key,
        video_ttl=30,
        enable_differential_privacy=True
    )
    
    # Simulate frame processing
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = {"lat": 9.0765, "lon": 7.3986, "accuracy_m": 3}
    metadata = {"altitude": 120, "weather": "clear"}
    
    request = processor.create_match_request(dummy_frame, location, metadata)
    
    if request:
        logger.info(f"Match request created: {request['device_id']}")
        logger.info(f"Template encrypted: {len(request['template'])} bytes")
