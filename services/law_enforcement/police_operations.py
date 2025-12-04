"""
Police Operations and Highway Patrol Management System

World-class AI security for law enforcement operations:
- Real-time officer tracking and dispatch
- Highway patrol monitoring and coordination
- Emergency response management
- Officer safety and backup coordination
- Crime pattern analysis and predictive policing
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
import uuid

# Geospatial and routing
try:
    import geopy.distance
    from geopy.geocoders import Nominatim
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OfficerStatus(Enum):
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    RESPONDING = "responding"
    BUSY = "busy"
    BACKUP_NEEDED = "backup_needed"
    EMERGENCY = "emergency"


class IncidentPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class VehicleType(Enum):
    PATROL_CAR = "patrol_car"
    MOTORCYCLE = "motorcycle"
    K9_UNIT = "k9_unit"
    SWAT_VEHICLE = "swat_vehicle"
    TRAFFIC_UNIT = "traffic_unit"
    HELICOPTER = "helicopter"


@dataclass
class PoliceOfficer:
    officer_id: str
    badge_number: str
    name: str
    rank: str
    division: str
    specializations: List[str]
    current_location: Tuple[float, float]
    status: OfficerStatus
    shift_start: datetime
    shift_end: datetime
    vehicle_id: Optional[str] = None
    partner_id: Optional[str] = None
    radio_frequency: str = "MAIN"
    last_check_in: Optional[datetime] = None


@dataclass
class PatrolVehicle:
    vehicle_id: str
    vehicle_type: VehicleType
    license_plate: str
    current_location: Tuple[float, float]
    assigned_officers: List[str]
    fuel_level_percent: float
    mileage: int
    equipment: List[str]
    status: str = "operational"
    last_maintenance: Optional[datetime] = None


@dataclass
class Incident:
    incident_id: str
    incident_type: str
    priority: IncidentPriority
    location: Tuple[float, float]
    address: str
    description: str
    caller_info: Dict[str, str]
    timestamp: datetime
    assigned_officers: List[str]
    response_time_minutes: Optional[int] = None
    status: str = "open"
    evidence: List[str] = None


@dataclass
class HighwayPatrolPost:
    post_id: str
    highway_name: str
    mile_marker_start: float
    mile_marker_end: float
    patrol_area_km2: float
    assigned_officers: List[str]
    average_traffic_volume: int
    accident_hotspots: List[Tuple[float, float]]
    speed_limit_zones: List[Tuple[float, float, int]]  # (start, end, speed_limit)


class DispatchSystem:
    """Intelligent dispatch system for optimal resource allocation"""
    
    def __init__(self):
        self.officers = {}
        self.vehicles = {}
        self.incidents = {}
        self.highway_posts = {}
        self.dispatch_queue = []
    
    def register_officer(self, officer: PoliceOfficer):
        """Register a police officer in the system"""
        self.officers[officer.officer_id] = officer
        logger.info(f"Registered Officer {officer.badge_number} - {officer.name}")
    
    def register_vehicle(self, vehicle: PatrolVehicle):
        """Register a patrol vehicle in the system"""
        self.vehicles[vehicle.vehicle_id] = vehicle
        logger.info(f"Registered Vehicle {vehicle.license_plate} - {vehicle.vehicle_type.value}")
    
    def create_incident(self, 
                       incident_type: str,
                       priority: IncidentPriority,
                       location: Tuple[float, float],
                       address: str,
                       description: str,
                       caller_info: Dict[str, str]) -> str:
        """Create a new incident and add to dispatch queue"""
        
        incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.incidents):04d}"
        
        incident = Incident(
            incident_id=incident_id,
            incident_type=incident_type,
            priority=priority,
            location=location,
            address=address,
            description=description,
            caller_info=caller_info,
            timestamp=datetime.now(),
            assigned_officers=[],
            evidence=[]
        )
        
        self.incidents[incident_id] = incident
        self.dispatch_queue.append(incident_id)
        self.dispatch_queue.sort(key=lambda x: self._get_priority_score(self.incidents[x].priority), reverse=True)
        
        logger.info(f"Created incident {incident_id}: {incident_type} - {priority.value}")
        return incident_id
    
    def dispatch_officers(self, incident_id: str) -> List[str]:
        """Dispatch optimal officers to an incident"""
        
        if incident_id not in self.incidents:
            logger.error(f"Incident {incident_id} not found")
            return []
        
        incident = self.incidents[incident_id]
        
        # Find available officers
        available_officers = [
            officer for officer in self.officers.values()
            if officer.status in [OfficerStatus.ON_DUTY, OfficerStatus.RESPONDING]
        ]
        
        if not available_officers:
            logger.warning("No available officers for dispatch")
            return []
        
        # Calculate optimal assignment based on distance and specialization
        officer_scores = []
        for officer in available_officers:
            score = self._calculate_officer_score(officer, incident)
            officer_scores.append((officer.officer_id, score))
        
        # Sort by score and select top officers
        officer_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Determine number of officers needed
        officers_needed = self._get_officers_needed(incident.priority, incident.incident_type)
        selected_officers = [score[0] for score in officer_scores[:officers_needed]]
        
        # Assign officers to incident
        incident.assigned_officers = selected_officers
        for officer_id in selected_officers:
            self.officers[officer_id].status = OfficerStatus.RESPONDING
        
        # Remove from dispatch queue
        if incident_id in self.dispatch_queue:
            self.dispatch_queue.remove(incident_id)
        
        logger.info(f"Dispatched {len(selected_officers)} officers to incident {incident_id}")
        return selected_officers
    
    def _calculate_officer_score(self, officer: PoliceOfficer, incident: Incident) -> float:
        """Calculate optimal assignment score for officer-incident pair"""
        
        score = 0.0
        
        # Distance factor (closer is better)
        if GEOSPATIAL_AVAILABLE:
            distance_km = geopy.distance.geodesic(officer.current_location, incident.location).kilometers
            distance_score = max(0, 10 - distance_km)  # Max score for <1km, decreases linearly
        else:
            # Simplified distance calculation
            lat_diff = abs(officer.current_location[0] - incident.location[0])
            lon_diff = abs(officer.current_location[1] - incident.location[1])
            distance_score = max(0, 10 - (lat_diff + lon_diff) * 100)
        
        score += distance_score
        
        # Specialization match
        incident_specializations = self._get_required_specializations(incident.incident_type)
        for specialization in incident_specializations:
            if specialization in officer.specializations:
                score += 5.0
        
        # Availability factor
        if officer.status == OfficerStatus.ON_DUTY:
            score += 3.0
        elif officer.status == OfficerStatus.RESPONDING:
            score += 1.0
        
        # Partner preference (keep partners together)
        if officer.partner_id and officer.partner_id in self.officers:
            partner = self.officers[officer.partner_id]
            if partner.status in [OfficerStatus.ON_DUTY, OfficerStatus.RESPONDING]:
                score += 2.0
        
        return score
    
    def _get_priority_score(self, priority: IncidentPriority) -> int:
        """Get numerical score for incident priority"""
        priority_scores = {
            IncidentPriority.EMERGENCY: 10,
            IncidentPriority.URGENT: 8,
            IncidentPriority.HIGH: 6,
            IncidentPriority.MEDIUM: 4,
            IncidentPriority.LOW: 2
        }
        return priority_scores.get(priority, 0)
    
    def _get_officers_needed(self, priority: IncidentPriority, incident_type: str) -> int:
        """Determine number of officers needed for incident"""
        
        # High-risk incidents need more officers
        high_risk_types = ['armed_robbery', 'domestic_violence', 'gang_activity', 'drug_raid']
        
        if incident_type in high_risk_types or priority == IncidentPriority.EMERGENCY:
            return 3
        elif priority in [IncidentPriority.URGENT, IncidentPriority.HIGH]:
            return 2
        else:
            return 1
    
    def _get_required_specializations(self, incident_type: str) -> List[str]:
        """Get required specializations for incident type"""
        
        specialization_map = {
            'drug_raid': ['narcotics', 'swat'],
            'domestic_violence': ['domestic_violence', 'crisis_intervention'],
            'traffic_accident': ['traffic', 'accident_investigation'],
            'gang_activity': ['gang_unit', 'swat'],
            'cybercrime': ['cybercrime', 'digital_forensics'],
            'k9_search': ['k9_handler'],
            'crowd_control': ['riot_control', 'crowd_management']
        }
        
        return specialization_map.get(incident_type, [])
    
    def update_officer_location(self, officer_id: str, location: Tuple[float, float]):
        """Update officer's current location"""
        if officer_id in self.officers:
            self.officers[officer_id].current_location = location
            self.officers[officer_id].last_check_in = datetime.now()
    
    def get_officer_status(self, officer_id: str) -> Dict[str, Any]:
        """Get comprehensive officer status"""
        
        if officer_id not in self.officers:
            return {'error': 'Officer not found'}
        
        officer = self.officers[officer_id]
        
        # Calculate shift progress
        shift_duration = (officer.shift_end - officer.shift_start).total_seconds()
        elapsed = (datetime.now() - officer.shift_start).total_seconds()
        shift_progress = min(100, (elapsed / shift_duration) * 100) if shift_duration > 0 else 0
        
        # Get current assignment
        current_incident = None
        for incident in self.incidents.values():
            if officer_id in incident.assigned_officers and incident.status == 'open':
                current_incident = {
                    'incident_id': incident.incident_id,
                    'type': incident.incident_type,
                    'priority': incident.priority.value,
                    'address': incident.address
                }
                break
        
        return {
            'officer_id': officer_id,
            'badge_number': officer.badge_number,
            'name': officer.name,
            'rank': officer.rank,
            'division': officer.division,
            'status': officer.status.value,
            'current_location': officer.current_location,
            'shift_progress_percent': shift_progress,
            'current_assignment': current_incident,
            'partner_id': officer.partner_id,
            'vehicle_id': officer.vehicle_id,
            'specializations': officer.specializations,
            'last_check_in': officer.last_check_in.isoformat() if officer.last_check_in else None
        }


class HighwayPatrolSystem:
    """Highway patrol monitoring and coordination system"""
    
    def __init__(self):
        self.patrol_posts = {}
        self.traffic_incidents = {}
        self.speed_violations = []
        self.patrol_schedules = {}
    
    def register_patrol_post(self, post: HighwayPatrolPost):
        """Register a highway patrol post"""
        self.patrol_posts[post.post_id] = post
        logger.info(f"Registered patrol post {post.post_id} on {post.highway_name}")
    
    def report_traffic_incident(self, 
                               highway: str,
                               mile_marker: float,
                               incident_type: str,
                               severity: str,
                               description: str) -> str:
        """Report a traffic incident on highway"""
        
        incident_id = f"HWY_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.traffic_incidents):04d}"
        
        incident = {
            'incident_id': incident_id,
            'highway': highway,
            'mile_marker': mile_marker,
            'incident_type': incident_type,
            'severity': severity,
            'description': description,
            'timestamp': datetime.now(),
            'lanes_affected': 1 if severity == 'minor' else 2 if severity == 'major' else 3,
            'estimated_clearance_time': self._estimate_clearance_time(incident_type, severity),
            'traffic_backup_km': 0,
            'status': 'active'
        }
        
        self.traffic_incidents[incident_id] = incident
        
        # Find nearest patrol post
        nearest_post = self._find_nearest_patrol_post(highway, mile_marker)
        if nearest_post:
            incident['assigned_post'] = nearest_post.post_id
        
        logger.info(f"Traffic incident reported: {incident_type} at {highway} MM{mile_marker}")
        return incident_id
    
    def _find_nearest_patrol_post(self, highway: str, mile_marker: float) -> Optional[HighwayPatrolPost]:
        """Find nearest patrol post to incident location"""
        
        matching_posts = [
            post for post in self.patrol_posts.values()
            if post.highway_name == highway and 
            post.mile_marker_start <= mile_marker <= post.mile_marker_end
        ]
        
        if matching_posts:
            return matching_posts[0]  # First matching post
        
        # Find closest post on same highway
        highway_posts = [post for post in self.patrol_posts.values() if post.highway_name == highway]
        if highway_posts:
            closest_post = min(highway_posts, 
                             key=lambda p: min(abs(p.mile_marker_start - mile_marker), 
                                             abs(p.mile_marker_end - mile_marker)))
            return closest_post
        
        return None
    
    def _estimate_clearance_time(self, incident_type: str, severity: str) -> int:
        """Estimate incident clearance time in minutes"""
        
        base_times = {
            'vehicle_breakdown': 30,
            'minor_accident': 45,
            'major_accident': 120,
            'multi_vehicle_accident': 180,
            'hazmat_spill': 240,
            'debris_removal': 20,
            'construction': 480
        }
        
        severity_multipliers = {
            'minor': 1.0,
            'major': 1.5,
            'severe': 2.0
        }
        
        base_time = base_times.get(incident_type, 60)
        multiplier = severity_multipliers.get(severity, 1.0)
        
        return int(base_time * multiplier)
    
    def get_highway_status(self, highway: str) -> Dict[str, Any]:
        """Get comprehensive highway status"""
        
        # Get all incidents on this highway
        highway_incidents = [
            incident for incident in self.traffic_incidents.values()
            if incident['highway'] == highway and incident['status'] == 'active'
        ]
        
        # Calculate traffic impact
        total_lanes_affected = sum(incident['lanes_affected'] for incident in highway_incidents)
        
        # Get patrol posts
        highway_posts = [post for post in self.patrol_posts.values() if post.highway_name == highway]
        
        return {
            'highway': highway,
            'active_incidents': len(highway_incidents),
            'total_lanes_affected': total_lanes_affected,
            'patrol_posts': len(highway_posts),
            'traffic_status': 'heavy' if total_lanes_affected > 5 else 'moderate' if total_lanes_affected > 2 else 'normal',
            'recent_incidents': [
                {
                    'incident_id': i['incident_id'],
                    'type': i['incident_type'],
                    'mile_marker': i['mile_marker'],
                    'severity': i['severity'],
                    'estimated_clearance': i['estimated_clearance_time']
                } for i in highway_incidents[-5:]  # Last 5 incidents
            ],
            'patrol_coverage': {
                'posts': [
                    {
                        'post_id': post.post_id,
                        'coverage_km': post.mile_marker_end - post.mile_marker_start,
                        'officers_assigned': len(post.assigned_officers)
                    } for post in highway_posts
                ]
            }
        }


class PoliceOperationsSystem:
    """Comprehensive police operations management system"""
    
    def __init__(self):
        self.dispatch_system = DispatchSystem()
        self.highway_patrol = HighwayPatrolSystem()
        self.crime_analytics = {}
        self.shift_schedules = {}
    
    def get_department_overview(self, state: str = None) -> Dict[str, Any]:
        """Get comprehensive department overview"""
        
        total_officers = len(self.dispatch_system.officers)
        on_duty_officers = len([o for o in self.dispatch_system.officers.values() if o.status != OfficerStatus.OFF_DUTY])
        
        # Incident statistics
        total_incidents = len(self.dispatch_system.incidents)
        open_incidents = len([i for i in self.dispatch_system.incidents.values() if i.status == 'open'])
        
        # Calculate response time statistics
        resolved_incidents = [i for i in self.dispatch_system.incidents.values() if i.response_time_minutes is not None]
        avg_response_time = np.mean([i.response_time_minutes for i in resolved_incidents]) if resolved_incidents else 0
        
        # Highway patrol status
        highway_incidents = len(self.highway_patrol.traffic_incidents)
        patrol_posts = len(self.highway_patrol.patrol_posts)
        
        return {
            'department_overview': {
                'total_officers': total_officers,
                'on_duty_officers': on_duty_officers,
                'duty_ratio_percent': (on_duty_officers / total_officers * 100) if total_officers > 0 else 0,
                'available_vehicles': len([v for v in self.dispatch_system.vehicles.values() if v.status == 'operational']),
                'total_vehicles': len(self.dispatch_system.vehicles)
            },
            'incident_management': {
                'total_incidents_24h': total_incidents,
                'open_incidents': open_incidents,
                'average_response_time_minutes': avg_response_time,
                'incidents_in_queue': len(self.dispatch_system.dispatch_queue),
                'priority_breakdown': self._get_priority_breakdown()
            },
            'highway_patrol': {
                'patrol_posts': patrol_posts,
                'active_highway_incidents': highway_incidents,
                'highways_monitored': len(set(post.highway_name for post in self.highway_patrol.patrol_posts.values()))
            },
            'performance_metrics': {
                'officer_utilization_percent': self._calculate_officer_utilization(),
                'vehicle_utilization_percent': self._calculate_vehicle_utilization(),
                'system_health_score': self._calculate_system_health()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_priority_breakdown(self) -> Dict[str, int]:
        """Get breakdown of incidents by priority"""
        priority_counts = {}
        for incident in self.dispatch_system.incidents.values():
            if incident.status == 'open':
                priority = incident.priority.value
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
        return priority_counts
    
    def _calculate_officer_utilization(self) -> float:
        """Calculate officer utilization percentage"""
        if not self.dispatch_system.officers:
            return 0.0
        
        busy_officers = len([
            o for o in self.dispatch_system.officers.values()
            if o.status in [OfficerStatus.RESPONDING, OfficerStatus.BUSY]
        ])
        
        total_on_duty = len([
            o for o in self.dispatch_system.officers.values()
            if o.status != OfficerStatus.OFF_DUTY
        ])
        
        return (busy_officers / total_on_duty * 100) if total_on_duty > 0 else 0.0
    
    def _calculate_vehicle_utilization(self) -> float:
        """Calculate vehicle utilization percentage"""
        if not self.dispatch_system.vehicles:
            return 0.0
        
        in_use_vehicles = len([
            v for v in self.dispatch_system.vehicles.values()
            if len(v.assigned_officers) > 0 and v.status == 'operational'
        ])
        
        operational_vehicles = len([
            v for v in self.dispatch_system.vehicles.values()
            if v.status == 'operational'
        ])
        
        return (in_use_vehicles / operational_vehicles * 100) if operational_vehicles > 0 else 0.0
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        score = 100.0
        
        # Deduct for long-pending incidents
        pending_incidents = len(self.dispatch_system.dispatch_queue)
        score -= min(pending_incidents * 2, 20)
        
        # Deduct for low officer availability
        officer_availability = (100 - self._calculate_officer_utilization()) / 100
        if officer_availability < 0.3:  # Less than 30% available
            score -= 15
        
        return max(0, score)


# Example usage and testing
if __name__ == "__main__":
    
    async def demo_police_operations():
        """Demonstrate police operations system"""
        
        print("👮 POLICE OPERATIONS AND HIGHWAY PATROL SYSTEM")
        print("=" * 60)
        
        # Initialize system
        police_system = PoliceOperationsSystem()
        
        # Register sample officers
        officers = [
            PoliceOfficer("OFF001", "1001", "John Smith", "Sergeant", "Patrol", 
                         ["traffic", "accident_investigation"], (40.7128, -74.0060), 
                         OfficerStatus.ON_DUTY, datetime.now() - timedelta(hours=2), 
                         datetime.now() + timedelta(hours=6), "VEH001"),
            PoliceOfficer("OFF002", "1002", "Sarah Johnson", "Officer", "Patrol", 
                         ["domestic_violence", "crisis_intervention"], (40.7589, -73.9851), 
                         OfficerStatus.ON_DUTY, datetime.now() - timedelta(hours=1), 
                         datetime.now() + timedelta(hours=7), "VEH002"),
            PoliceOfficer("OFF003", "1003", "Mike Davis", "Detective", "Narcotics", 
                         ["narcotics", "undercover"], (40.8176, -73.9782), 
                         OfficerStatus.ON_DUTY, datetime.now() - timedelta(hours=3), 
                         datetime.now() + timedelta(hours=5), "VEH003")
        ]
        
        for officer in officers:
            police_system.dispatch_system.register_officer(officer)
        
        # Register sample vehicles
        vehicles = [
            PatrolVehicle("VEH001", VehicleType.PATROL_CAR, "POLICE-001", (40.7128, -74.0060), 
                         ["OFF001"], 85.0, 45000, ["radio", "laptop", "first_aid"]),
            PatrolVehicle("VEH002", VehicleType.PATROL_CAR, "POLICE-002", (40.7589, -73.9851), 
                         ["OFF002"], 72.0, 38000, ["radio", "laptop", "breathalyzer"]),
            PatrolVehicle("VEH003", VehicleType.K9_UNIT, "POLICE-K9-001", (40.8176, -73.9782), 
                         ["OFF003"], 68.0, 52000, ["radio", "k9_equipment", "search_tools"])
        ]
        
        for vehicle in vehicles:
            police_system.dispatch_system.register_vehicle(vehicle)
        
        # Register highway patrol post
        highway_post = HighwayPatrolPost(
            post_id="HWY001",
            highway_name="I-95",
            mile_marker_start=10.0,
            mile_marker_end=25.0,
            patrol_area_km2=50.0,
            assigned_officers=["OFF001"],
            average_traffic_volume=50000,
            accident_hotspots=[(40.7300, -73.9900), (40.7400, -73.9800)],
            speed_limit_zones=[(10.0, 15.0, 65), (15.0, 25.0, 55)]
        )
        
        police_system.highway_patrol.register_patrol_post(highway_post)
        
        print("✅ Police operations system initialized")
        print(f"   - Officers: {len(officers)}")
        print(f"   - Vehicles: {len(vehicles)}")
        print(f"   - Highway Posts: 1")
        
        # Create sample incidents
        print("\n🚨 Creating sample incidents...")
        
        incidents = [
            ("domestic_violence", IncidentPriority.HIGH, (40.7200, -74.0000), 
             "123 Main St", "Domestic disturbance reported", {"caller": "neighbor", "phone": "555-0001"}),
            ("traffic_accident", IncidentPriority.MEDIUM, (40.7500, -73.9900), 
             "I-95 Mile 15", "Two-car accident blocking right lane", {"caller": "driver", "phone": "555-0002"}),
            ("armed_robbery", IncidentPriority.EMERGENCY, (40.7800, -73.9700), 
             "456 Oak Ave", "Armed robbery in progress", {"caller": "store_owner", "phone": "555-0003"})
        ]
        
        created_incidents = []
        for incident_type, priority, location, address, description, caller_info in incidents:
            incident_id = police_system.dispatch_system.create_incident(
                incident_type, priority, location, address, description, caller_info
            )
            created_incidents.append(incident_id)
        
        # Dispatch officers
        print("\n🚁 Dispatching officers to incidents...")
        for incident_id in created_incidents:
            assigned_officers = police_system.dispatch_system.dispatch_officers(incident_id)
            incident = police_system.dispatch_system.incidents[incident_id]
            print(f"   📍 {incident.incident_type} - {len(assigned_officers)} officers dispatched")
        
        # Report highway incident
        print("\n🛣️ Reporting highway traffic incident...")
        highway_incident_id = police_system.highway_patrol.report_traffic_incident(
            "I-95", 18.5, "major_accident", "major", "Multi-vehicle accident with injuries"
        )
        
        # Get officer status
        print("\n👮 Officer Status Updates:")
        for officer_id in ["OFF001", "OFF002"]:
            status = police_system.dispatch_system.get_officer_status(officer_id)
            print(f"   Officer {status['badge_number']} ({status['name']}):")
            print(f"      Status: {status['status']}")
            print(f"      Location: {status['current_location']}")
            if status['current_assignment']:
                print(f"      Assignment: {status['current_assignment']['type']} ({status['current_assignment']['priority']})")
        
        # Get highway status
        print("\n🛣️ Highway Status:")
        highway_status = police_system.highway_patrol.get_highway_status("I-95")
        print(f"   Highway: {highway_status['highway']}")
        print(f"   Active Incidents: {highway_status['active_incidents']}")
        print(f"   Traffic Status: {highway_status['traffic_status']}")
        print(f"   Patrol Posts: {highway_status['patrol_posts']}")
        
        # Department overview
        print("\n🏢 Department Overview:")
        overview = police_system.get_department_overview()
        print(f"   Officers: {overview['department_overview']['on_duty_officers']}/{overview['department_overview']['total_officers']} on duty")
        print(f"   Vehicles: {overview['department_overview']['available_vehicles']}/{overview['department_overview']['total_vehicles']} available")
        print(f"   Response Time: {overview['incident_management']['average_response_time_minutes']:.1f} minutes")
        print(f"   Officer Utilization: {overview['performance_metrics']['officer_utilization_percent']:.1f}%")
        print(f"   System Health: {overview['performance_metrics']['system_health_score']:.1f}/100")
    
    # Run demo
    asyncio.run(demo_police_operations())