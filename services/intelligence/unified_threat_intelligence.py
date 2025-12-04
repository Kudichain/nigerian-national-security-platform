"""
Unified Threat Intelligence Layer
World-Class AI Security Platform - Knowledge Graph Engine

Fuses all data sources into a single unified knowledge graph:
- CCTV surveillance feeds
- Drone aerial monitoring
- Citizen ID verification
- Vehicle tracking
- Network intrusion detection
- Phishing attempts
- Malware incidents
- Authentication anomalies
- Infrastructure monitoring

Uses Neo4j-style graph relationships for cross-correlation and threat detection.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import json
import hashlib
from enum import Enum

app = FastAPI(
    title="🧠 Unified Threat Intelligence",
    version="2.0.0",
    description="World-Class Knowledge Graph for National Security Cross-Correlation"
)

# ============================================================================
# KNOWLEDGE GRAPH DATA STRUCTURES
# ============================================================================

class EntityType(str, Enum):
    PERSON = "person"
    VEHICLE = "vehicle"
    LOCATION = "location"
    DEVICE = "device"
    NETWORK = "network"
    ORGANIZATION = "organization"
    INCIDENT = "incident"
    THREAT = "threat"

class RelationType(str, Enum):
    ASSOCIATED_WITH = "associated_with"
    LOCATED_AT = "located_at"
    OWNS = "owns"
    OPERATES = "operates"
    CONNECTED_TO = "connected_to"
    PART_OF = "part_of"
    TRIGGERED = "triggered"
    DETECTED_BY = "detected_by"

class ThreatCategory(str, Enum):
    CYBER = "cyber"
    PHYSICAL = "physical"
    HYBRID = "hybrid"
    INSIDER = "insider"
    TERRORISM = "terrorism"
    ORGANIZED_CRIME = "organized_crime"
    FRAUD = "fraud"

# Knowledge Graph Storage (Replace with Neo4j in production)
KNOWLEDGE_GRAPH = {
    "entities": {},  # entity_id -> Entity
    "relationships": defaultdict(list),  # entity_id -> [(relation_type, target_id, metadata)]
    "incidents": {},  # incident_id -> Incident
    "correlations": [],  # List of detected correlations
}

# ============================================================================
# MODELS
# ============================================================================

class Entity(BaseModel):
    entity_id: str = Field(..., description="Unique entity identifier")
    entity_type: EntityType
    attributes: Dict[str, Any]
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    threat_indicators: List[str] = []
    data_sources: List[str] = []

class Relationship(BaseModel):
    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class ThreatCorrelation(BaseModel):
    correlation_id: str
    threat_category: ThreatCategory
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float
    entities_involved: List[str]
    relationships: List[str]
    timeline: List[datetime]
    description: str
    recommended_actions: List[str]
    evidence: Dict[str, Any]

class DataIngestion(BaseModel):
    source: str = Field(..., description="cctv, drone, vehicle, citizen_id, nids, phishing, etc.")
    entity_type: EntityType
    entity_id: str
    attributes: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# ============================================================================
# CROSS-CORRELATION ENGINE
# ============================================================================

class CrossCorrelationEngine:
    """Advanced AI engine for detecting patterns across multiple data sources"""
    
    def __init__(self):
        self.correlation_rules = self._initialize_rules()
        self.active_investigations = {}
    
    def _initialize_rules(self) -> List[Dict[str, Any]]:
        """Define correlation rules for threat detection"""
        return [
            {
                "name": "Coordinated Attack Pattern",
                "description": "Multiple individuals at different locations accessing same target",
                "conditions": [
                    "multiple_persons",
                    "different_locations",
                    "same_target_network",
                    "short_timeframe"
                ],
                "severity": "CRITICAL",
                "category": ThreatCategory.TERRORISM
            },
            {
                "name": "Vehicle + Person Association",
                "description": "Flagged vehicle repeatedly seen with persons of interest",
                "conditions": [
                    "flagged_vehicle",
                    "person_of_interest",
                    "repeated_encounters"
                ],
                "severity": "HIGH",
                "category": ThreatCategory.ORGANIZED_CRIME
            },
            {
                "name": "Insider Threat Pattern",
                "description": "Authorized person accessing unusual systems + communication anomalies",
                "conditions": [
                    "authorized_access",
                    "unusual_systems",
                    "communication_anomaly",
                    "data_exfiltration"
                ],
                "severity": "CRITICAL",
                "category": ThreatCategory.INSIDER
            },
            {
                "name": "Physical-Cyber Convergence",
                "description": "Physical surveillance of critical infrastructure + cyber reconnaissance",
                "conditions": [
                    "physical_surveillance",
                    "cyber_reconnaissance",
                    "critical_infrastructure",
                    "temporal_correlation"
                ],
                "severity": "CRITICAL",
                "category": ThreatCategory.HYBRID
            },
            {
                "name": "Identity Fraud Ring",
                "description": "Multiple fraudulent IDs from same location with similar patterns",
                "conditions": [
                    "multiple_fake_ids",
                    "same_location",
                    "similar_patterns",
                    "shared_biometrics"
                ],
                "severity": "HIGH",
                "category": ThreatCategory.FRAUD
            }
        ]
    
    async def analyze_entity(self, entity: Entity) -> List[ThreatCorrelation]:
        """Analyze entity for threat correlations"""
        correlations = []
        
        # Find all relationships for this entity
        relationships = KNOWLEDGE_GRAPH["relationships"].get(entity.entity_id, [])
        
        # Apply correlation rules
        for rule in self.correlation_rules:
            if self._matches_rule(entity, relationships, rule):
                correlation = await self._create_correlation(entity, rule, relationships)
                correlations.append(correlation)
        
        return correlations
    
    def _matches_rule(self, entity: Entity, relationships: List, rule: Dict) -> bool:
        """Check if entity and relationships match correlation rule"""
        # Simplified rule matching (implement full logic based on conditions)
        if entity.risk_score > 0.7:
            # High-risk entities trigger deeper analysis
            return len(relationships) >= 3
        return False
    
    async def _create_correlation(
        self, 
        entity: Entity, 
        rule: Dict, 
        relationships: List
    ) -> ThreatCorrelation:
        """Create threat correlation from matched rule"""
        correlation_id = hashlib.sha256(
            f"{entity.entity_id}{rule['name']}{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # Find all entities involved
        entities_involved = [entity.entity_id]
        for rel_type, target_id, metadata in relationships:
            entities_involved.append(target_id)
        
        # Generate recommended actions based on severity
        actions = self._generate_actions(rule['severity'], rule['category'])
        
        return ThreatCorrelation(
            correlation_id=correlation_id,
            threat_category=rule['category'],
            severity=rule['severity'],
            confidence=0.85,
            entities_involved=entities_involved,
            relationships=[str(r) for r in relationships],
            timeline=[entity.first_seen, entity.last_seen],
            description=rule['description'],
            recommended_actions=actions,
            evidence={
                "rule": rule['name'],
                "entity_risk_score": entity.risk_score,
                "relationship_count": len(relationships),
                "threat_indicators": entity.threat_indicators
            }
        )
    
    def _generate_actions(self, severity: str, category: ThreatCategory) -> List[str]:
        """Generate recommended actions based on threat"""
        base_actions = [
            "🔴 Alert security operations center immediately",
            "📊 Gather additional intelligence from all connected systems",
            "👥 Notify relevant law enforcement agencies"
        ]
        
        if severity == "CRITICAL":
            base_actions.extend([
                "🚨 Initiate emergency response protocol",
                "🔒 Implement containment measures",
                "📞 Brief senior leadership within 15 minutes"
            ])
        
        if category == ThreatCategory.TERRORISM:
            base_actions.append("🏛️ Coordinate with DSS and Nigerian Army Intelligence")
        elif category == ThreatCategory.CYBER:
            base_actions.append("💻 Engage ngCERT and cybersecurity response team")
        
        return base_actions

# Global correlation engine
correlation_engine = CrossCorrelationEngine()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/v1/intelligence/ingest")
async def ingest_data(data: DataIngestion):
    """
    Ingest data from any source into unified knowledge graph
    
    Sources: cctv, drone, vehicle_tracking, citizen_id, nids, phishing, 
             auth_anomaly, malware, infrastructure, police_report
    """
    # Create or update entity
    entity = Entity(
        entity_id=data.entity_id,
        entity_type=data.entity_type,
        attributes=data.attributes,
        data_sources=[data.source],
        last_seen=data.timestamp
    )
    
    # Calculate risk score based on attributes
    entity.risk_score = _calculate_risk_score(data.attributes, data.source)
    
    # Store in knowledge graph
    if data.entity_id in KNOWLEDGE_GRAPH["entities"]:
        # Update existing entity
        existing = KNOWLEDGE_GRAPH["entities"][data.entity_id]
        existing.last_seen = data.timestamp
        existing.data_sources = list(set(existing.data_sources + [data.source]))
        existing.attributes.update(data.attributes)
        existing.risk_score = max(existing.risk_score, entity.risk_score)
        entity = existing
    else:
        # Create new entity
        KNOWLEDGE_GRAPH["entities"][data.entity_id] = entity
    
    # Run correlation analysis
    correlations = await correlation_engine.analyze_entity(entity)
    
    # Store significant correlations
    for corr in correlations:
        if corr.confidence > 0.75:
            KNOWLEDGE_GRAPH["correlations"].append(corr)
    
    return {
        "status": "success",
        "entity_id": data.entity_id,
        "risk_score": entity.risk_score,
        "correlations_detected": len(correlations),
        "threat_indicators": entity.threat_indicators
    }

@app.post("/api/v1/intelligence/relationship")
async def create_relationship(relationship: Relationship):
    """Create relationship between entities in knowledge graph"""
    # Verify both entities exist
    if relationship.source_id not in KNOWLEDGE_GRAPH["entities"]:
        raise HTTPException(404, f"Source entity {relationship.source_id} not found")
    if relationship.target_id not in KNOWLEDGE_GRAPH["entities"]:
        raise HTTPException(404, f"Target entity {relationship.target_id} not found")
    
    # Create bidirectional relationship
    KNOWLEDGE_GRAPH["relationships"][relationship.source_id].append(
        (relationship.relation_type, relationship.target_id, relationship.metadata)
    )
    KNOWLEDGE_GRAPH["relationships"][relationship.target_id].append(
        (relationship.relation_type, relationship.source_id, relationship.metadata)
    )
    
    return {
        "status": "success",
        "relationship": relationship.dict()
    }

@app.get("/api/v1/intelligence/correlations")
async def get_threat_correlations(
    severity: Optional[str] = None,
    category: Optional[ThreatCategory] = None,
    min_confidence: float = 0.7
):
    """Get all threat correlations with optional filtering"""
    correlations = KNOWLEDGE_GRAPH["correlations"]
    
    # Apply filters
    if severity:
        correlations = [c for c in correlations if c.severity == severity.upper()]
    if category:
        correlations = [c for c in correlations if c.threat_category == category]
    
    correlations = [c for c in correlations if c.confidence >= min_confidence]
    
    return {
        "total_correlations": len(correlations),
        "correlations": [c.dict() for c in correlations[-50:]]  # Last 50
    }

@app.get("/api/v1/intelligence/entity/{entity_id}")
async def get_entity_intelligence(entity_id: str):
    """Get complete intelligence profile for an entity"""
    if entity_id not in KNOWLEDGE_GRAPH["entities"]:
        raise HTTPException(404, "Entity not found")
    
    entity = KNOWLEDGE_GRAPH["entities"][entity_id]
    relationships = KNOWLEDGE_GRAPH["relationships"].get(entity_id, [])
    
    # Find correlations involving this entity
    correlations = [
        c for c in KNOWLEDGE_GRAPH["correlations"]
        if entity_id in c.entities_involved
    ]
    
    return {
        "entity": entity.dict(),
        "relationships": len(relationships),
        "connected_entities": len(set(r[1] for r in relationships)),
        "threat_correlations": len(correlations),
        "high_risk": entity.risk_score > 0.7,
        "timeline": {
            "first_seen": entity.first_seen,
            "last_seen": entity.last_seen,
            "duration_days": (entity.last_seen - entity.first_seen).days
        }
    }

@app.get("/api/v1/intelligence/network/{entity_id}")
async def get_entity_network(entity_id: str, depth: int = 2):
    """Get network graph around an entity (BFS traversal)"""
    if entity_id not in KNOWLEDGE_GRAPH["entities"]:
        raise HTTPException(404, "Entity not found")
    
    # Breadth-first search to build network
    visited = set()
    network = {"entities": [], "relationships": []}
    queue = [(entity_id, 0)]
    
    while queue:
        current_id, current_depth = queue.pop(0)
        
        if current_id in visited or current_depth > depth:
            continue
        
        visited.add(current_id)
        entity = KNOWLEDGE_GRAPH["entities"][current_id]
        network["entities"].append(entity.dict())
        
        # Add relationships
        for rel_type, target_id, metadata in KNOWLEDGE_GRAPH["relationships"].get(current_id, []):
            if target_id not in visited:
                network["relationships"].append({
                    "source": current_id,
                    "target": target_id,
                    "type": rel_type,
                    "metadata": metadata
                })
                queue.append((target_id, current_depth + 1))
    
    return {
        "root_entity": entity_id,
        "depth": depth,
        "network_size": len(network["entities"]),
        "network": network
    }

@app.get("/api/v1/intelligence/stats")
async def get_intelligence_stats():
    """Get knowledge graph statistics"""
    entities = KNOWLEDGE_GRAPH["entities"]
    relationships = KNOWLEDGE_GRAPH["relationships"]
    correlations = KNOWLEDGE_GRAPH["correlations"]
    
    # Calculate statistics
    high_risk_entities = sum(1 for e in entities.values() if e.risk_score > 0.7)
    
    entity_type_counts = defaultdict(int)
    for entity in entities.values():
        entity_type_counts[entity.entity_type] += 1
    
    severity_counts = defaultdict(int)
    for corr in correlations:
        severity_counts[corr.severity] += 1
    
    return {
        "knowledge_graph": {
            "total_entities": len(entities),
            "total_relationships": sum(len(rels) for rels in relationships.values()) // 2,
            "high_risk_entities": high_risk_entities,
            "entity_types": dict(entity_type_counts)
        },
        "threat_intelligence": {
            "total_correlations": len(correlations),
            "by_severity": dict(severity_counts),
            "critical_threats": severity_counts["CRITICAL"]
        },
        "data_quality": {
            "entities_with_multiple_sources": sum(
                1 for e in entities.values() if len(e.data_sources) > 1
            ),
            "average_risk_score": sum(e.risk_score for e in entities.values()) / len(entities) if entities else 0
        }
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_risk_score(attributes: Dict[str, Any], source: str) -> float:
    """Calculate risk score based on attributes and source"""
    score = 0.0
    
    # Source-specific risk indicators
    if source == "nids" and attributes.get("severity") == "critical":
        score += 0.4
    elif source == "phishing" and attributes.get("confidence") > 0.8:
        score += 0.3
    elif source == "malware" and attributes.get("threat_level") == "high":
        score += 0.5
    elif source == "auth_anomaly" and attributes.get("failed_attempts", 0) > 5:
        score += 0.3
    
    # General risk indicators
    if attributes.get("blacklisted"):
        score += 0.4
    if attributes.get("suspicious_behavior"):
        score += 0.2
    if attributes.get("known_threat"):
        score += 0.5
    
    return min(score, 1.0)

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "service": "unified-threat-intelligence",
        "version": "2.0.0",
        "knowledge_graph_size": len(KNOWLEDGE_GRAPH["entities"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
