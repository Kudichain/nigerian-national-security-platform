"""
Immigration and Airport Security System

World-class AI security for immigration control and airport terminals:
- Passport validation and document verification
- Biometric identity verification
- Immigration officer management and duty rosters
- Airport terminal security monitoring
- Customs inspection and risk assessment
- Passenger flow analysis and queue management
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
import uuid

# Document processing and OCR
try:
    import cv2
    from PIL import Image
    import pytesseract
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False

# Machine learning for risk assessment
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PassportStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    STOLEN = "stolen"
    FORGERY = "forgery"
    UNDER_REVIEW = "under_review"


class VisaStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    RESTRICTED = "restricted"
    PENDING = "pending"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OfficerDutyStatus(Enum):
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    BREAK = "break"
    TRAINING = "training"
    LEAVE = "leave"


@dataclass
class Passport:
    passport_number: str
    country_of_issue: str
    holder_name: str
    date_of_birth: datetime
    issue_date: datetime
    expiry_date: datetime
    biometric_data: Optional[Dict[str, str]] = None
    status: PassportStatus = PassportStatus.VALID
    security_features: Optional[List[str]] = None


@dataclass
class Visa:
    visa_number: str
    visa_type: str
    country_of_issue: str
    holder_passport: str
    issue_date: datetime
    expiry_date: datetime
    entries_allowed: int
    entries_used: int = 0
    restrictions: Optional[List[str]] = None
    status: VisaStatus = VisaStatus.VALID


@dataclass
class CitizenPassportApplication:
    application_id: str
    citizen_name: str
    citizen_id: str
    date_of_birth: datetime
    place_of_birth: str
    application_date: datetime
    documents_submitted: List[str]
    status: str  # pending, processing, approved, rejected, issued
    processing_officer: Optional[str] = None
    expected_completion: Optional[datetime] = None


@dataclass
class ImmigrationOfficer:
    officer_id: str
    name: str
    badge_number: str
    rank: str
    specializations: List[str]
    airport_terminal: str
    duty_status: OfficerDutyStatus
    shift_start: datetime
    shift_end: datetime
    languages_spoken: List[str]
    security_clearance_level: int


@dataclass
class AirportTerminal:
    terminal_id: str
    airport_code: str
    airport_name: str
    location: Tuple[float, float]
    terminal_name: str
    capacity_passengers_per_hour: int
    immigration_desks: int
    customs_lanes: int
    security_checkpoints: int
    assigned_officers: List[str]


@dataclass
class PassengerEntry:
    entry_id: str
    passport_number: str
    passenger_name: str
    flight_number: str
    origin_country: str
    arrival_time: datetime
    terminal_id: str
    immigration_officer: str
    entry_purpose: str
    risk_assessment: RiskLevel
    additional_screening: bool = False
    customs_declaration: Optional[Dict[str, Any]] = None


class PassportValidationEngine:
    """Advanced passport validation and document verification system"""
    
    def __init__(self):
        self.passport_database = {}
        self.stolen_passports = set()
        self.security_features = {
            'biometric_chip': True,
            'holographic_overlay': True,
            'microprinting': True,
            'security_thread': True,
            'uv_reactive_ink': True
        }
    
    def validate_passport(self, passport: Passport, document_image: Optional[bytes] = None) -> Dict[str, Any]:
        """Comprehensive passport validation"""
        
        validation_result = {
            'passport_number': passport.passport_number,
            'validation_timestamp': datetime.now(),
            'is_valid': True,
            'validation_checks': {},
            'risk_flags': [],
            'recommendations': []
        }
        
        # 1. Basic information validation
        validation_result['validation_checks']['expiry_check'] = self._check_expiry(passport)
        validation_result['validation_checks']['format_check'] = self._check_format(passport)
        validation_result['validation_checks']['country_check'] = self._check_issuing_country(passport)
        
        # 2. Security database checks
        validation_result['validation_checks']['stolen_check'] = self._check_stolen_database(passport)
        validation_result['validation_checks']['watchlist_check'] = self._check_watchlist(passport)
        
        # 3. Document authenticity (if image provided)
        if document_image and DOCUMENT_PROCESSING_AVAILABLE:
            validation_result['validation_checks']['authenticity_check'] = self._verify_document_authenticity(document_image)
        else:
            validation_result['validation_checks']['authenticity_check'] = {'status': 'not_performed', 'reason': 'no_image_or_cv_unavailable'}
        
        # 4. Biometric verification
        if passport.biometric_data:
            validation_result['validation_checks']['biometric_check'] = self._verify_biometrics(passport)
        
        # Determine overall validity
        failed_checks = [k for k, v in validation_result['validation_checks'].items() if v.get('status') == 'failed']
        
        if failed_checks:
            validation_result['is_valid'] = False
            validation_result['failed_checks'] = failed_checks
            
            # Determine passport status
            if 'stolen_check' in failed_checks:
                passport.status = PassportStatus.STOLEN
            elif 'expiry_check' in failed_checks:
                passport.status = PassportStatus.EXPIRED
            elif 'authenticity_check' in failed_checks:
                passport.status = PassportStatus.FORGERY
            else:
                passport.status = PassportStatus.INVALID
        
        return validation_result
    
    def _check_expiry(self, passport: Passport) -> Dict[str, Any]:
        """Check if passport is expired"""
        now = datetime.now()
        
        if passport.expiry_date < now:
            days_expired = (now - passport.expiry_date).days
            return {
                'status': 'failed',
                'reason': f'passport_expired_{days_expired}_days_ago',
                'expiry_date': passport.expiry_date.isoformat()
            }
        elif passport.expiry_date < now + timedelta(days=180):
            days_until_expiry = (passport.expiry_date - now).days
            return {
                'status': 'warning',
                'reason': f'passport_expires_in_{days_until_expiry}_days',
                'expiry_date': passport.expiry_date.isoformat()
            }
        else:
            return {
                'status': 'passed',
                'expiry_date': passport.expiry_date.isoformat()
            }
    
    def _check_format(self, passport: Passport) -> Dict[str, Any]:
        """Validate passport number format"""
        # Basic format validation (country-specific rules would be more complex)
        if len(passport.passport_number) < 6 or len(passport.passport_number) > 15:
            return {
                'status': 'failed',
                'reason': 'invalid_passport_number_format'
            }
        
        return {
            'status': 'passed',
            'format': 'valid'
        }
    
    def _check_issuing_country(self, passport: Passport) -> Dict[str, Any]:
        """Validate issuing country"""
        # List of recognized countries (simplified)
        valid_countries = ['USA', 'GBR', 'CAN', 'DEU', 'FRA', 'JPN', 'AUS', 'IND', 'CHN', 'BRA', 'MEX']
        
        if passport.country_of_issue in valid_countries:
            return {
                'status': 'passed',
                'issuing_country': passport.country_of_issue
            }
        else:
            return {
                'status': 'warning',
                'reason': 'unusual_issuing_country',
                'issuing_country': passport.country_of_issue
            }
    
    def _check_stolen_database(self, passport: Passport) -> Dict[str, Any]:
        """Check against stolen passport database"""
        if passport.passport_number in self.stolen_passports:
            return {
                'status': 'failed',
                'reason': 'passport_reported_stolen',
                'alert_level': 'critical'
            }
        
        return {
            'status': 'passed',
            'database_check': 'clear'
        }
    
    def _check_watchlist(self, passport: Passport) -> Dict[str, Any]:
        """Check holder against security watchlists"""
        # Mock watchlist check
        watchlist_names = ['John Doe Suspicious', 'Jane Smith Wanted']
        
        if passport.holder_name in watchlist_names:
            return {
                'status': 'failed',
                'reason': 'holder_on_watchlist',
                'alert_level': 'high'
            }
        
        return {
            'status': 'passed',
            'watchlist_check': 'clear'
        }
    
    def _verify_document_authenticity(self, document_image: bytes) -> Dict[str, Any]:
        """Verify document authenticity using image analysis"""
        # Mock document authenticity check
        # In production, this would use advanced image processing and ML
        
        authenticity_score = np.random.uniform(0.7, 1.0)  # Mock score
        
        if authenticity_score > 0.9:
            return {
                'status': 'passed',
                'authenticity_score': authenticity_score,
                'security_features_detected': list(self.security_features.keys())
            }
        elif authenticity_score > 0.7:
            return {
                'status': 'warning',
                'authenticity_score': authenticity_score,
                'reason': 'some_security_features_unclear'
            }
        else:
            return {
                'status': 'failed',
                'authenticity_score': authenticity_score,
                'reason': 'possible_document_forgery'
            }
    
    def _verify_biometrics(self, passport: Passport) -> Dict[str, Any]:
        """Verify biometric data"""
        # Mock biometric verification
        if passport.biometric_data:
            match_score = np.random.uniform(0.8, 1.0)
            
            if match_score > 0.95:
                return {
                    'status': 'passed',
                    'biometric_match_score': match_score,
                    'verification_type': 'facial_recognition'
                }
            else:
                return {
                    'status': 'warning',
                    'biometric_match_score': match_score,
                    'reason': 'biometric_match_below_threshold'
                }
        
        return {
            'status': 'not_performed',
            'reason': 'no_biometric_data'
        }


class RiskAssessmentEngine:
    """AI-powered passenger risk assessment system"""
    
    def __init__(self):
        self.risk_model = None
        self.risk_factors = {
            'origin_country_risk': 0.3,
            'travel_pattern_anomaly': 0.25,
            'document_issues': 0.2,
            'watchlist_match': 0.15,
            'behavioral_indicators': 0.1
        }
        
        if ML_AVAILABLE:
            self._initialize_risk_model()
    
    def _initialize_risk_model(self):
        """Initialize machine learning risk assessment model"""
        # Mock training data for demonstration
        np.random.seed(42)
        n_samples = 1000
        
        # Features: country_risk_score, document_score, travel_frequency, age
        X = np.random.rand(n_samples, 4)
        
        # Mock risk labels
        y = np.random.choice(['low', 'medium', 'high'], n_samples, p=[0.7, 0.25, 0.05])
        
        self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.risk_model.fit(X, y)
        
        logger.info("Risk assessment model initialized")
    
    def assess_passenger_risk(self, 
                             passport: Passport,
                             visa: Optional[Visa],
                             travel_history: List[Dict],
                             entry_purpose: str) -> Dict[str, Any]:
        """Comprehensive passenger risk assessment"""
        
        risk_assessment = {
            'passenger_name': passport.holder_name,
            'passport_number': passport.passport_number,
            'assessment_timestamp': datetime.now(),
            'overall_risk_level': RiskLevel.LOW,
            'risk_score': 0.0,
            'risk_factors': {},
            'recommendations': []
        }
        
        # 1. Country of origin risk
        origin_risk = self._assess_country_risk(passport.country_of_issue)
        risk_assessment['risk_factors']['origin_country'] = origin_risk
        
        # 2. Document validity risk
        doc_risk = self._assess_document_risk(passport, visa)
        risk_assessment['risk_factors']['document_validity'] = doc_risk
        
        # 3. Travel pattern analysis
        travel_risk = self._assess_travel_patterns(travel_history)
        risk_assessment['risk_factors']['travel_patterns'] = travel_risk
        
        # 4. Purpose of visit assessment
        purpose_risk = self._assess_visit_purpose(entry_purpose)
        risk_assessment['risk_factors']['visit_purpose'] = purpose_risk
        
        # Calculate overall risk score
        total_risk_score = (
            origin_risk['risk_score'] * self.risk_factors['origin_country_risk'] +
            doc_risk['risk_score'] * self.risk_factors['document_issues'] +
            travel_risk['risk_score'] * self.risk_factors['travel_pattern_anomaly'] +
            purpose_risk['risk_score'] * self.risk_factors['behavioral_indicators']
        )
        
        risk_assessment['risk_score'] = total_risk_score
        
        # Determine risk level
        if total_risk_score > 0.8:
            risk_assessment['overall_risk_level'] = RiskLevel.CRITICAL
            risk_assessment['recommendations'] = ['secondary_inspection', 'supervisor_review', 'detailed_questioning']
        elif total_risk_score > 0.6:
            risk_assessment['overall_risk_level'] = RiskLevel.HIGH
            risk_assessment['recommendations'] = ['additional_screening', 'document_verification', 'baggage_inspection']
        elif total_risk_score > 0.4:
            risk_assessment['overall_risk_level'] = RiskLevel.MEDIUM
            risk_assessment['recommendations'] = ['random_additional_questions', 'document_review']
        else:
            risk_assessment['overall_risk_level'] = RiskLevel.LOW
            risk_assessment['recommendations'] = ['standard_processing']
        
        return risk_assessment
    
    def _assess_country_risk(self, country: str) -> Dict[str, Any]:
        """Assess risk based on country of origin"""
        # Simplified country risk scoring
        high_risk_countries = ['Country1', 'Country2']  # Placeholder
        medium_risk_countries = ['Country3', 'Country4']
        
        if country in high_risk_countries:
            return {'risk_score': 0.8, 'category': 'high_risk_origin'}
        elif country in medium_risk_countries:
            return {'risk_score': 0.5, 'category': 'medium_risk_origin'}
        else:
            return {'risk_score': 0.2, 'category': 'standard_origin'}
    
    def _assess_document_risk(self, passport: Passport, visa: Optional[Visa]) -> Dict[str, Any]:
        """Assess risk based on document status"""
        if passport.status != PassportStatus.VALID:
            return {'risk_score': 0.9, 'reason': f'passport_status_{passport.status.value}'}
        
        if visa and visa.status != VisaStatus.VALID:
            return {'risk_score': 0.7, 'reason': f'visa_status_{visa.status.value}'}
        
        # Check expiry proximity
        days_until_expiry = (passport.expiry_date - datetime.now()).days
        if days_until_expiry < 30:
            return {'risk_score': 0.4, 'reason': 'passport_expires_soon'}
        
        return {'risk_score': 0.1, 'status': 'documents_valid'}
    
    def _assess_travel_patterns(self, travel_history: List[Dict]) -> Dict[str, Any]:
        """Assess risk based on travel patterns"""
        if not travel_history:
            return {'risk_score': 0.3, 'reason': 'no_travel_history'}
        
        # Look for unusual patterns
        countries_visited = len(set(trip['country'] for trip in travel_history))
        recent_trips = len([trip for trip in travel_history 
                          if datetime.fromisoformat(trip['date']) > datetime.now() - timedelta(days=90)])
        
        if recent_trips > 5:
            return {'risk_score': 0.6, 'reason': 'frequent_recent_travel'}
        elif countries_visited > 10:
            return {'risk_score': 0.4, 'reason': 'extensive_travel_history'}
        else:
            return {'risk_score': 0.2, 'status': 'normal_travel_pattern'}
    
    def _assess_visit_purpose(self, purpose: str) -> Dict[str, Any]:
        """Assess risk based on stated purpose of visit"""
        high_risk_purposes = ['business_meeting_unclear', 'visiting_friends_no_details']
        medium_risk_purposes = ['business', 'education']
        
        if purpose in high_risk_purposes:
            return {'risk_score': 0.7, 'category': 'high_risk_purpose'}
        elif purpose in medium_risk_purposes:
            return {'risk_score': 0.3, 'category': 'medium_risk_purpose'}
        else:
            return {'risk_score': 0.1, 'category': 'standard_purpose'}


class AirportImmigrationSystem:
    """Comprehensive airport immigration and customs system"""
    
    def __init__(self):
        self.passport_validator = PassportValidationEngine()
        self.risk_assessor = RiskAssessmentEngine()
        self.terminals = {}
        self.officers = {}
        self.passenger_applications = {}
        self.immigration_stats = {
            'total_applications': 0,
            'pending_applications': 0,
            'approved_applications': 0,
            'rejected_applications': 0,
            'issued_passports': 0
        }
        self.entry_logs = []
    
    def register_terminal(self, terminal: AirportTerminal):
        """Register an airport terminal"""
        self.terminals[terminal.terminal_id] = terminal
        logger.info(f"Registered terminal {terminal.terminal_name} at {terminal.airport_name}")
    
    def register_immigration_officer(self, officer: ImmigrationOfficer):
        """Register an immigration officer"""
        self.officers[officer.officer_id] = officer
        logger.info(f"Registered Immigration Officer {officer.name} - {officer.rank}")
    
    def process_passport_application(self, application: CitizenPassportApplication) -> str:
        """Process a new passport application"""
        self.passenger_applications[application.application_id] = application
        self.immigration_stats['total_applications'] += 1
        self.immigration_stats['pending_applications'] += 1
        
        # Assign processing officer
        available_officers = [
            o for o in self.officers.values() 
            if o.duty_status == OfficerDutyStatus.ON_DUTY and 'passport_processing' in o.specializations
        ]
        
        if available_officers:
            application.processing_officer = available_officers[0].officer_id
            application.expected_completion = datetime.now() + timedelta(days=14)
            application.status = 'processing'
        
        logger.info(f"Processing passport application {application.application_id}")
        return application.application_id
    
    def process_passenger_entry(self,
                               passport: Passport,
                               visa: Optional[Visa],
                               flight_number: str,
                               terminal_id: str,
                               entry_purpose: str) -> Dict[str, Any]:
        """Process passenger entry through immigration"""
        
        if terminal_id not in self.terminals:
            return {'error': 'Terminal not found'}
        
        terminal = self.terminals[terminal_id]
        
        # Validate passport
        passport_validation = self.passport_validator.validate_passport(passport)
        
        # Assess risk
        risk_assessment = self.risk_assessor.assess_passenger_risk(
            passport, visa, [], entry_purpose
        )
        
        # Find available immigration officer
        available_officers = [
            o for o in self.officers.values()
            if o.duty_status == OfficerDutyStatus.ON_DUTY and o.airport_terminal == terminal_id
        ]
        
        if not available_officers:
            return {'error': 'No immigration officers available'}
        
        assigned_officer = available_officers[0]
        
        # Create passenger entry record
        entry = PassengerEntry(
            entry_id=f"ENTRY_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.entry_logs):04d}",
            passport_number=passport.passport_number,
            passenger_name=passport.holder_name,
            flight_number=flight_number,
            origin_country=passport.country_of_issue,
            arrival_time=datetime.now(),
            terminal_id=terminal_id,
            immigration_officer=assigned_officer.officer_id,
            entry_purpose=entry_purpose,
            risk_assessment=risk_assessment['overall_risk_level'],
            additional_screening=risk_assessment['overall_risk_level'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        self.entry_logs.append(entry)
        
        # Determine processing outcome
        processing_result = {
            'entry_id': entry.entry_id,
            'passport_validation': passport_validation,
            'risk_assessment': risk_assessment,
            'immigration_officer': {
                'name': assigned_officer.name,
                'badge_number': assigned_officer.badge_number
            },
            'additional_screening_required': entry.additional_screening,
            'estimated_processing_time_minutes': self._estimate_processing_time(risk_assessment['overall_risk_level']),
            'entry_status': 'approved' if passport_validation['is_valid'] and risk_assessment['overall_risk_level'] != RiskLevel.CRITICAL else 'under_review',
            'timestamp': datetime.now().isoformat()
        }
        
        return processing_result
    
    def get_terminal_status(self, terminal_id: str) -> Dict[str, Any]:
        """Get comprehensive terminal status"""
        
        if terminal_id not in self.terminals:
            return {'error': 'Terminal not found'}
        
        terminal = self.terminals[terminal_id]
        
        # Count officers on duty
        on_duty_officers = [
            o for o in self.officers.values()
            if o.airport_terminal == terminal_id and o.duty_status == OfficerDutyStatus.ON_DUTY
        ]
        
        # Recent entries (last 24 hours)
        recent_entries = [
            e for e in self.entry_logs
            if e.terminal_id == terminal_id and e.arrival_time >= datetime.now() - timedelta(hours=24)
        ]
        
        # Calculate security metrics
        high_risk_entries = len([e for e in recent_entries if e.risk_assessment in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        additional_screenings = len([e for e in recent_entries if e.additional_screening])
        
        return {
            'terminal_id': terminal_id,
            'terminal_name': terminal.terminal_name,
            'airport': terminal.airport_name,
            'officers_on_duty': len(on_duty_officers),
            'total_officers_assigned': len(terminal.assigned_officers),
            'immigration_desks_available': terminal.immigration_desks,
            'entries_24h': len(recent_entries),
            'high_risk_entries_24h': high_risk_entries,
            'additional_screenings_24h': additional_screenings,
            'current_capacity_utilization': min(100, len(recent_entries) / terminal.capacity_passengers_per_hour * 100),
            'security_level': 'elevated' if high_risk_entries > 5 else 'normal',
            'officers_status': [
                {
                    'name': o.name,
                    'rank': o.rank,
                    'duty_status': o.duty_status.value,
                    'specializations': o.specializations
                } for o in on_duty_officers
            ]
        }
    
    def get_national_immigration_overview(self) -> Dict[str, Any]:
        """Get national overview of immigration operations"""
        
        total_terminals = len(self.terminals)
        total_officers = len(self.officers)
        on_duty_officers = len([o for o in self.officers.values() if o.duty_status == OfficerDutyStatus.ON_DUTY])
        
        # Passport application statistics
        approval_rate = 0
        if self.immigration_stats['total_applications'] > 0:
            approval_rate = (self.immigration_stats['approved_applications'] / self.immigration_stats['total_applications']) * 100
        
        # Recent entry statistics
        recent_entries = [e for e in self.entry_logs if e.arrival_time >= datetime.now() - timedelta(hours=24)]
        
        return {
            'national_immigration_system': {
                'total_airports': len(set(t.airport_code for t in self.terminals.values())),
                'total_terminals': total_terminals,
                'total_immigration_officers': total_officers,
                'officers_on_duty': on_duty_officers,
                'officer_utilization_percent': (on_duty_officers / total_officers * 100) if total_officers > 0 else 0
            },
            'passport_services': {
                'total_applications': self.immigration_stats['total_applications'],
                'pending_applications': self.immigration_stats['pending_applications'],
                'approved_applications': self.immigration_stats['approved_applications'],
                'rejected_applications': self.immigration_stats['rejected_applications'],
                'issued_passports': self.immigration_stats['issued_passports'],
                'approval_rate_percent': approval_rate,
                'average_processing_time_days': 14  # Standard processing time
            },
            'border_security': {
                'total_entries_24h': len(recent_entries),
                'high_risk_entries_24h': len([e for e in recent_entries if e.risk_assessment in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
                'additional_screenings_24h': len([e for e in recent_entries if e.additional_screening]),
                'countries_of_origin': list(set(e.origin_country for e in recent_entries)),
                'system_security_level': self._calculate_national_security_level(recent_entries)
            },
            'performance_metrics': {
                'average_processing_time_minutes': np.mean([self._estimate_processing_time(e.risk_assessment) for e in recent_entries]) if recent_entries else 5,
                'system_health_score': self._calculate_system_health(),
                'passport_validation_success_rate': 95.0  # Mock rate
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _estimate_processing_time(self, risk_level: RiskLevel) -> int:
        """Estimate processing time based on risk level"""
        processing_times = {
            RiskLevel.LOW: 3,
            RiskLevel.MEDIUM: 8,
            RiskLevel.HIGH: 15,
            RiskLevel.CRITICAL: 30
        }
        return processing_times.get(risk_level, 5)
    
    def _calculate_national_security_level(self, recent_entries: List[PassengerEntry]) -> str:
        """Calculate national immigration security level"""
        if not recent_entries:
            return "NORMAL"
        
        critical_entries = len([e for e in recent_entries if e.risk_assessment == RiskLevel.CRITICAL])
        high_risk_entries = len([e for e in recent_entries if e.risk_assessment == RiskLevel.HIGH])
        
        if critical_entries > 2 or high_risk_entries > 10:
            return "ELEVATED"
        elif critical_entries > 0 or high_risk_entries > 5:
            return "GUARDED"
        else:
            return "NORMAL"
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        score = 100.0
        
        # Deduct for high pending applications
        pending_ratio = self.immigration_stats['pending_applications'] / max(self.immigration_stats['total_applications'], 1)
        if pending_ratio > 0.3:
            score -= 15
        
        # Deduct for officer availability
        total_officers = len(self.officers)
        on_duty = len([o for o in self.officers.values() if o.duty_status == OfficerDutyStatus.ON_DUTY])
        if total_officers > 0 and (on_duty / total_officers) < 0.6:
            score -= 10
        
        return max(0, score)


# Example usage and testing
if __name__ == "__main__":
    
    async def demo_immigration_system():
        """Demonstrate immigration and airport security system"""
        
        print("✈️ IMMIGRATION AND AIRPORT SECURITY SYSTEM")
        print("=" * 60)
        
        # Initialize system
        immigration_system = AirportImmigrationSystem()
        
        # Register sample terminal
        terminal = AirportTerminal(
            terminal_id="T1_JFK",
            airport_code="JFK",
            airport_name="John F. Kennedy International Airport",
            location=(40.6413, -73.7781),
            terminal_name="Terminal 1",
            capacity_passengers_per_hour=500,
            immigration_desks=12,
            customs_lanes=8,
            security_checkpoints=6,
            assigned_officers=["OFF001", "OFF002", "OFF003"]
        )
        
        immigration_system.register_terminal(terminal)
        
        # Register immigration officers
        officers = [
            ImmigrationOfficer("OFF001", "Alice Johnson", "IM-001", "Senior Inspector", 
                             ["passport_processing", "document_verification", "risk_assessment"],
                             "T1_JFK", OfficerDutyStatus.ON_DUTY, 
                             datetime.now() - timedelta(hours=2), datetime.now() + timedelta(hours=6),
                             ["English", "Spanish", "French"], 3),
            ImmigrationOfficer("OFF002", "Bob Martinez", "IM-002", "Inspector",
                             ["customs_inspection", "baggage_screening", "secondary_inspection"],
                             "T1_JFK", OfficerDutyStatus.ON_DUTY,
                             datetime.now() - timedelta(hours=1), datetime.now() + timedelta(hours=7),
                             ["English", "Portuguese"], 2),
            ImmigrationOfficer("OFF003", "Carol Wong", "IM-003", "Supervisor",
                             ["passport_processing", "supervisory_review", "training"],
                             "T1_JFK", OfficerDutyStatus.ON_DUTY,
                             datetime.now() - timedelta(hours=3), datetime.now() + timedelta(hours=5),
                             ["English", "Mandarin", "Cantonese"], 4)
        ]
        
        for officer in officers:
            immigration_system.register_immigration_officer(officer)
        
        print("✅ Immigration system initialized")
        print(f"   - Airport: {terminal.airport_name}")
        print(f"   - Terminal: {terminal.terminal_name}")
        print(f"   - Immigration Officers: {len(officers)}")
        
        # Create sample passport applications
        print("\n📄 Processing passport applications...")
        
        applications = [
            CitizenPassportApplication("APP001", "John Smith", "SSN123456789", 
                                     datetime(1985, 5, 15), "New York, NY", datetime.now(),
                                     ["birth_certificate", "photo_id", "application_form"], "pending"),
            CitizenPassportApplication("APP002", "Maria Garcia", "SSN987654321",
                                     datetime(1990, 8, 22), "Los Angeles, CA", datetime.now(),
                                     ["birth_certificate", "photo_id", "application_form"], "pending"),
            CitizenPassportApplication("APP003", "David Chen", "SSN456789123",
                                     datetime(1988, 12, 3), "San Francisco, CA", datetime.now(),
                                     ["naturalization_certificate", "photo_id", "application_form"], "pending")
        ]
        
        for app in applications:
            app_id = immigration_system.process_passport_application(app)
            print(f"   📄 Application {app_id} - {app.citizen_name}")
        
        # Process passenger entries
        print("\n🛂 Processing passenger entries...")
        
        # Create sample passports
        passports = [
            Passport("US123456789", "USA", "Robert Johnson", datetime(1980, 3, 10),
                    datetime(2020, 1, 1), datetime(2030, 1, 1)),
            Passport("GB987654321", "GBR", "Emma Thompson", datetime(1985, 7, 20),
                    datetime(2019, 6, 15), datetime(2029, 6, 15)),
            Passport("FR456789123", "FRA", "Pierre Dubois", datetime(1975, 11, 5),
                    datetime(2021, 3, 10), datetime(2031, 3, 10))
        ]
        
        entries = []
        for i, passport in enumerate(passports):
            entry_result = immigration_system.process_passenger_entry(
                passport, None, f"AA{100+i}", "T1_JFK", "tourism"
            )
            
            entries.append(entry_result)
            print(f"   🛂 {passport.holder_name} ({passport.country_of_issue})")
            print(f"      Status: {entry_result['entry_status']}")
            print(f"      Risk: {entry_result['risk_assessment']['overall_risk_level'].value}")
            print(f"      Additional screening: {entry_result['additional_screening_required']}")
        
        # Get terminal status
        print("\n🏢 Terminal Status:")
        terminal_status = immigration_system.get_terminal_status("T1_JFK")
        print(f"   Terminal: {terminal_status['terminal_name']}")
        print(f"   Officers on duty: {terminal_status['officers_on_duty']}")
        print(f"   Entries (24h): {terminal_status['entries_24h']}")
        print(f"   High-risk entries: {terminal_status['high_risk_entries_24h']}")
        print(f"   Security level: {terminal_status['security_level']}")
        
        # National overview
        print("\n🇺🇸 National Immigration Overview:")
        overview = immigration_system.get_national_immigration_overview()
        print(f"   System Status: {overview['national_immigration_system']}")
        print(f"   Passport Services: Applications: {overview['passport_services']['total_applications']}, Approval Rate: {overview['passport_services']['approval_rate_percent']:.1f}%")
        print(f"   Border Security: Entries (24h): {overview['border_security']['total_entries_24h']}, Security Level: {overview['border_security']['system_security_level']}")
        print(f"   Performance: Health Score: {overview['performance_metrics']['system_health_score']:.1f}/100")
    
    # Run demo
    asyncio.run(demo_immigration_system())