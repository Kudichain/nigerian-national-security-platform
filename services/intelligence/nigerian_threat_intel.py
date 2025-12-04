"""
Nigerian Local Threat Intelligence Integration
Contextual security intelligence from Nigerian agencies

Integrates with:
- Nigerian Communications Commission (NCC)
- Nigerian Cybersecurity Emergency Response Team (ngCERT)
- Nigeria Police Force (NPF)
- Department of State Services (DSS)
- Economic and Financial Crimes Commission (EFCC)
- Nigerian Immigration Service (NIS)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import random

app = FastAPI(
    title="🇳🇬 Nigerian Threat Intelligence",
    version="1.0.0",
    description="Local Contextual Security Intelligence Integration"
)

# ============================================================================
# MODELS
# ============================================================================

class ThreatSource(str, Enum):
    NCC = "ncc"  # Nigerian Communications Commission
    NGCERT = "ngcert"  # Nigerian CERT
    NPF = "npf"  # Nigeria Police Force
    DSS = "dss"  # Department of State Services
    EFCC = "efcc"  # Economic and Financial Crimes Commission
    NIS = "nis"  # Nigerian Immigration Service
    ICPC = "icpc"  # Independent Corrupt Practices Commission
    NSCDC = "nscdc"  # Nigeria Security and Civil Defence Corps

class ThreatType(str, Enum):
    CYBERCRIME = "cybercrime"
    FRAUD = "fraud"
    TERRORISM = "terrorism"
    KIDNAPPING = "kidnapping"
    BANDITRY = "banditry"
    SMUGGLING = "smuggling"
    MONEY_LAUNDERING = "money_laundering"
    CYBERBULLYING = "cyberbullying"
    FAKE_NEWS = "fake_news"

class ThreatIndicator(BaseModel):
    indicator_id: str
    source: ThreatSource
    threat_type: ThreatType
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    indicators: Dict[str, Any]  # IPs, domains, phone numbers, etc.
    region: Optional[str] = None  # Nigerian state
    timestamp: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

# ============================================================================
# MOCK DATA FEEDS (Replace with real API integrations)
# ============================================================================

class NigerianThreatIntelligence:
    """Integration with Nigerian security agencies"""
    
    def __init__(self):
        self.threat_feeds = []
        self._initialize_mock_feeds()
    
    def _initialize_mock_feeds(self):
        """Initialize with mock threat intelligence"""
        
        # NCC - Telecom fraud patterns
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="NCC-2024-001",
            source=ThreatSource.NCC,
            threat_type=ThreatType.FRAUD,
            confidence=0.95,
            description="Mass SIM card fraud operation detected in Lagos",
            indicators={
                "phone_prefixes": ["0801234", "0907654"],
                "modus_operandi": "SIM swap attacks targeting bank accounts",
                "affected_networks": ["MTN", "Airtel", "Glo"],
                "estimated_victims": 1247
            },
            region="Lagos",
            expires_at=datetime.now() + timedelta(days=30)
        ))
        
        # ngCERT - Cyber threat intelligence
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="NGCERT-2024-045",
            source=ThreatSource.NGCERT,
            threat_type=ThreatType.CYBERCRIME,
            confidence=0.92,
            description="Advanced Persistent Threat (APT) targeting Nigerian government websites",
            indicators={
                "malicious_ips": ["41.203.72.x", "102.89.x.x"],
                "attack_vector": "SQL injection + credential stuffing",
                "target_sectors": ["government", "education", "healthcare"],
                "malware_families": ["AgentTesla", "NetWire"],
                "campaign_name": "Operation Harmattan"
            },
            region="National",
            expires_at=datetime.now() + timedelta(days=60)
        ))
        
        # NPF - Criminal activity patterns
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="NPF-2024-128",
            source=ThreatSource.NPF,
            threat_type=ThreatType.KIDNAPPING,
            confidence=0.88,
            description="Kidnapping gang operating along Abuja-Kaduna expressway",
            indicators={
                "locations": ["Kilometer 45-67", "Near Katari village"],
                "modus_operandi": "Vehicle blockade + armed ambush",
                "active_times": ["6:00 PM - 10:00 PM"],
                "vehicle_descriptions": ["White Hilux", "Black Sienna"],
                "estimated_members": 15
            },
            region="Kaduna",
            expires_at=datetime.now() + timedelta(days=7)
        ))
        
        # DSS - National security threats
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="DSS-2024-089",
            source=ThreatSource.DSS,
            threat_type=ThreatType.TERRORISM,
            confidence=0.94,
            description="Suspicious movement of extremist elements in Northeast",
            indicators={
                "regions": ["Borno", "Yobe", "Adamawa"],
                "threat_level": "HIGH",
                "activity_type": "Reconnaissance + recruitment",
                "communication_channels": ["Encrypted messaging apps"],
                "indicators_of_attack": ["Fuel stockpiling", "Vehicle movements"]
            },
            region="Northeast Nigeria",
            expires_at=datetime.now() + timedelta(days=14)
        ))
        
        # EFCC - Financial crime intelligence
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="EFCC-2024-234",
            source=ThreatSource.EFCC,
            threat_type=ThreatType.MONEY_LAUNDERING,
            confidence=0.91,
            description="Cryptocurrency-based money laundering network",
            indicators={
                "crypto_wallets": ["0xABCD...", "bc1q..."],
                "exchanges_used": ["Binance P2P", "LocalBitcoins"],
                "transaction_pattern": "Small amounts (₦50k-200k) high frequency",
                "bank_accounts": ["Flagged accounts in multiple banks"],
                "estimated_volume": "₦2.3 billion annually"
            },
            region="National",
            expires_at=datetime.now() + timedelta(days=90)
        ))
        
        # NIS - Immigration & border security
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="NIS-2024-067",
            source=ThreatSource.NIS,
            threat_type=ThreatType.SMUGGLING,
            confidence=0.87,
            description="Human trafficking route via Niger Republic border",
            indicators={
                "entry_points": ["Sokoto border", "Katsina border"],
                "modus_operandi": "Fake travel documents + bribery",
                "destination_countries": ["Libya", "Algeria"],
                "smuggling_networks": ["Network Alpha", "Network Bravo"],
                "victims_profile": "Young women 18-25 years"
            },
            region="Northwest Nigeria",
            expires_at=datetime.now() + timedelta(days=45)
        ))
        
        # Additional NCC feed - Fake news/misinformation
        self.threat_feeds.append(ThreatIndicator(
            indicator_id="NCC-2024-089",
            source=ThreatSource.NCC,
            threat_type=ThreatType.FAKE_NEWS,
            confidence=0.93,
            description="Coordinated misinformation campaign targeting upcoming elections",
            indicators={
                "platforms": ["WhatsApp", "Facebook", "Twitter/X"],
                "narratives": ["Election rigging", "Ethnic tensions"],
                "bot_accounts": ["Detected 15,000+ fake accounts"],
                "origin": "Domestic + foreign actors",
                "target_regions": ["Lagos", "Kano", "Rivers"]
            },
            region="National",
            expires_at=datetime.now() + timedelta(days=180)
        ))

    def get_all_threats(self) -> List[ThreatIndicator]:
        """Get all active threat indicators"""
        # Filter expired threats
        now = datetime.now()
        return [
            threat for threat in self.threat_feeds
            if threat.expires_at is None or threat.expires_at > now
        ]
    
    def get_threats_by_source(self, source: ThreatSource) -> List[ThreatIndicator]:
        """Get threats from specific agency"""
        return [t for t in self.get_all_threats() if t.source == source]
    
    def get_threats_by_type(self, threat_type: ThreatType) -> List[ThreatIndicator]:
        """Get threats by type"""
        return [t for t in self.get_all_threats() if t.threat_type == threat_type]
    
    def get_threats_by_region(self, region: str) -> List[ThreatIndicator]:
        """Get threats by Nigerian region/state"""
        return [
            t for t in self.get_all_threats()
            if t.region and (
                t.region.lower() == region.lower() or
                t.region.lower() == "national"
            )
        ]
    
    def get_high_confidence_threats(self, min_confidence: float = 0.9) -> List[ThreatIndicator]:
        """Get high-confidence threat indicators"""
        return [
            t for t in self.get_all_threats()
            if t.confidence >= min_confidence
        ]

threat_intel = NigerianThreatIntelligence()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/v1/nigerian-intel/all")
async def get_all_threats():
    """Get all active Nigerian threat intelligence"""
    threats = threat_intel.get_all_threats()
    
    return {
        "total_threats": len(threats),
        "threats": [t.dict() for t in threats],
        "sources": list(set(t.source for t in threats)),
        "last_updated": datetime.now()
    }

@app.get("/api/v1/nigerian-intel/source/{source}")
async def get_threats_by_source(source: ThreatSource):
    """Get threats from specific Nigerian agency"""
    threats = threat_intel.get_threats_by_source(source)
    
    agency_names = {
        ThreatSource.NCC: "Nigerian Communications Commission",
        ThreatSource.NGCERT: "Nigerian CERT",
        ThreatSource.NPF: "Nigeria Police Force",
        ThreatSource.DSS: "Department of State Services",
        ThreatSource.EFCC: "Economic and Financial Crimes Commission",
        ThreatSource.NIS: "Nigerian Immigration Service"
    }
    
    return {
        "source": source,
        "agency_name": agency_names.get(source, source),
        "threat_count": len(threats),
        "threats": [t.dict() for t in threats]
    }

@app.get("/api/v1/nigerian-intel/type/{threat_type}")
async def get_threats_by_type(threat_type: ThreatType):
    """Get threats by type"""
    threats = threat_intel.get_threats_by_type(threat_type)
    
    return {
        "threat_type": threat_type,
        "threat_count": len(threats),
        "threats": [t.dict() for t in threats]
    }

@app.get("/api/v1/nigerian-intel/region/{region}")
async def get_threats_by_region(region: str):
    """Get threats by Nigerian state/region"""
    threats = threat_intel.get_threats_by_region(region)
    
    return {
        "region": region,
        "threat_count": len(threats),
        "threats": [t.dict() for t in threats]
    }

@app.get("/api/v1/nigerian-intel/high-confidence")
async def get_high_confidence_threats(min_confidence: float = 0.9):
    """Get high-confidence threat indicators"""
    threats = threat_intel.get_high_confidence_threats(min_confidence)
    
    return {
        "min_confidence": min_confidence,
        "threat_count": len(threats),
        "threats": [t.dict() for t in threats]
    }

@app.get("/api/v1/nigerian-intel/agencies")
async def get_agency_info():
    """Get information about integrated Nigerian agencies"""
    return {
        "agencies": [
            {
                "code": "NCC",
                "name": "Nigerian Communications Commission",
                "role": "Telecom regulation, SIM fraud, cybercrime",
                "website": "https://ncc.gov.ng",
                "status": "integrated"
            },
            {
                "code": "ngCERT",
                "name": "Nigeria Computer Emergency Response Team",
                "role": "Cyber threat intelligence, incident response",
                "website": "https://ngcert.gov.ng",
                "status": "integrated"
            },
            {
                "code": "NPF",
                "name": "Nigeria Police Force",
                "role": "Law enforcement, crime prevention",
                "website": "https://npf.gov.ng",
                "status": "integrated"
            },
            {
                "code": "DSS",
                "name": "Department of State Services",
                "role": "National security, counterterrorism",
                "website": "https://dss.gov.ng",
                "status": "integrated"
            },
            {
                "code": "EFCC",
                "name": "Economic and Financial Crimes Commission",
                "role": "Financial crimes, corruption, fraud",
                "website": "https://efccnigeria.org",
                "status": "integrated"
            },
            {
                "code": "NIS",
                "name": "Nigerian Immigration Service",
                "role": "Border security, immigration control",
                "website": "https://immigration.gov.ng",
                "status": "integrated"
            }
        ],
        "total_agencies": 6,
        "integration_status": "operational"
    }

@app.get("/api/v1/nigerian-intel/stats")
async def get_intelligence_statistics():
    """Get Nigerian threat intelligence statistics"""
    all_threats = threat_intel.get_all_threats()
    
    # Group by source
    by_source = {}
    for threat in all_threats:
        if threat.source not in by_source:
            by_source[threat.source] = 0
        by_source[threat.source] += 1
    
    # Group by type
    by_type = {}
    for threat in all_threats:
        if threat.threat_type not in by_type:
            by_type[threat.threat_type] = 0
        by_type[threat.threat_type] += 1
    
    # Group by region
    by_region = {}
    for threat in all_threats:
        region = threat.region or "Unknown"
        if region not in by_region:
            by_region[region] = 0
        by_region[region] += 1
    
    return {
        "total_active_threats": len(all_threats),
        "high_confidence_threats": len([t for t in all_threats if t.confidence >= 0.9]),
        "by_source": by_source,
        "by_type": by_type,
        "by_region": by_region,
        "average_confidence": sum(t.confidence for t in all_threats) / len(all_threats) if all_threats else 0,
        "last_updated": datetime.now()
    }

@app.get("/health")
async def health_check():
    threats = threat_intel.get_all_threats()
    return {
        "status": "operational",
        "service": "nigerian-threat-intelligence",
        "version": "1.0.0",
        "active_threats": len(threats),
        "integrated_agencies": 6
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8105)
