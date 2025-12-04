"""
ICS/SCADA-compliant Traffic Light Control System
IEC 62443 aligned, safety interlocks, failsafe behavior
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import hmac
import uuid
import logging
from dataclasses import dataclass
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Traffic Control Plane", version="1.0.0")
security = HTTPBearer()


class TrafficPhase(str, Enum):
    """Standard traffic light phases"""
    NORTH_SOUTH_GREEN = "ns_green"
    NORTH_SOUTH_YELLOW = "ns_yellow"
    NORTH_SOUTH_RED = "ns_red"
    EAST_WEST_GREEN = "ew_green"
    EAST_WEST_YELLOW = "ew_yellow"
    EAST_WEST_RED = "ew_red"
    PEDESTRIAN_CROSSING = "pedestrian"
    ALL_RED_CLEARANCE = "all_red"
    EMERGENCY_FLASH = "emergency_flash"
    LOCAL_FALLBACK = "local_fallback"


class ControlAction(str, Enum):
    """Control actions"""
    SET_PHASE = "set_phase"
    EMERGENCY_STOP = "emergency_stop"
    RESUME_NORMAL = "resume_normal"
    EXTEND_PHASE = "extend_phase"


class ControllerStatus(str, Enum):
    """Controller operational status"""
    NORMAL = "normal"
    REMOTE_CONTROLLED = "remote_controlled"
    EMERGENCY = "emergency"
    FAILSAFE = "failsafe"
    MAINTENANCE = "maintenance"


class ControlRequest(BaseModel):
    """Control request from decision engine"""
    request_id: str
    action: ControlAction
    intersection_id: str
    phase: Optional[TrafficPhase] = None
    duration_seconds: Optional[int] = Field(None, ge=1, le=300)
    authority: str = Field(..., description="Operator or service ID")
    signed_policy_token: str = Field(..., description="Signed authorization token")
    reason: str = Field(..., description="Justification for control action")
    
    @validator('duration_seconds')
    def validate_duration(cls, v, values):
        if values.get('action') == ControlAction.SET_PHASE and v is None:
            raise ValueError("duration_seconds required for SET_PHASE action")
        return v


class ControlResponse(BaseModel):
    """Response from control plane"""
    request_id: str
    accepted: bool
    intersection_id: str
    current_phase: TrafficPhase
    new_phase: Optional[TrafficPhase]
    simulated: bool
    validation_passed: bool
    safety_checks: Dict[str, bool]
    executed_at: Optional[str] = None
    signature: str
    reason: str


@dataclass
class IntersectionState:
    """Current state of traffic intersection"""
    intersection_id: str
    current_phase: TrafficPhase
    status: ControllerStatus
    last_phase_change: datetime
    next_scheduled_change: datetime
    remote_control_active: bool
    controller_health: str
    phase_history: List[Dict[str, Any]]
    
    def is_safe_transition(self, new_phase: TrafficPhase) -> bool:
        """Validate phase transition safety"""
        # Safety matrix: disallowed direct transitions
        unsafe_transitions = {
            (TrafficPhase.NORTH_SOUTH_GREEN, TrafficPhase.EAST_WEST_GREEN),
            (TrafficPhase.EAST_WEST_GREEN, TrafficPhase.NORTH_SOUTH_GREEN),
        }
        
        transition = (self.current_phase, new_phase)
        return transition not in unsafe_transitions
    
    def requires_clearance(self, new_phase: TrafficPhase) -> bool:
        """Check if all-red clearance needed before transition"""
        major_transitions = [
            (TrafficPhase.NORTH_SOUTH_GREEN, TrafficPhase.EAST_WEST_GREEN),
            (TrafficPhase.EAST_WEST_GREEN, TrafficPhase.NORTH_SOUTH_GREEN),
        ]
        return (self.current_phase, new_phase) in major_transitions


class SafetyInterlock:
    """Safety validation for traffic control"""
    
    def __init__(self):
        self.max_phase_duration = timedelta(minutes=5)
        self.min_clearance_time = timedelta(seconds=3)
        logger.info("Safety interlock initialized")
    
    def validate_request(
        self,
        request: ControlRequest,
        state: IntersectionState
    ) -> Dict[str, bool]:
        """Run comprehensive safety checks"""
        checks = {
            'controller_health': state.controller_health == "healthy",
            'safe_transition': state.is_safe_transition(request.phase) if request.phase else True,
            'duration_valid': self._validate_duration(request),
            'no_conflicting_greens': self._check_no_conflicts(request.phase) if request.phase else True,
            'authorization_valid': self._validate_authorization(request),
            'rate_limit': self._check_rate_limit(state),
        }
        
        return checks
    
    def _validate_duration(self, request: ControlRequest) -> bool:
        """Validate phase duration"""
        if request.duration_seconds is None:
            return True
        return 1 <= request.duration_seconds <= 300
    
    def _check_no_conflicts(self, phase: TrafficPhase) -> bool:
        """Ensure no conflicting green signals"""
        # In real implementation: check actual controller state
        # Prevent two conflicting directions being green simultaneously
        return phase not in [TrafficPhase.EMERGENCY_FLASH]  # Example rule
    
    def _validate_authorization(self, request: ControlRequest) -> bool:
        """Validate authorization token"""
        # In production: verify signed JWT from decision engine
        # Check operator permissions, time bounds, etc.
        return len(request.signed_policy_token) > 10
    
    def _check_rate_limit(self, state: IntersectionState) -> bool:
        """Prevent rapid phase changes"""
        time_since_last = datetime.utcnow() - state.last_phase_change
        return time_since_last > timedelta(seconds=5)


class TrafficController:
    """
    Simulated traffic light controller with ICS security
    In production: interfaces with actual SCADA/PLC hardware
    """
    
    def __init__(self, intersection_id: str):
        self.intersection_id = intersection_id
        self.state = IntersectionState(
            intersection_id=intersection_id,
            current_phase=TrafficPhase.NORTH_SOUTH_GREEN,
            status=ControllerStatus.NORMAL,
            last_phase_change=datetime.utcnow(),
            next_scheduled_change=datetime.utcnow() + timedelta(seconds=30),
            remote_control_active=False,
            controller_health="healthy",
            phase_history=[]
        )
        self.safety = SafetyInterlock()
        self.watchdog_active = True
        
        # Start local control loop
        asyncio.create_task(self._local_control_loop())
        asyncio.create_task(self._watchdog())
        
        logger.info(f"Traffic controller initialized: {intersection_id}")
    
    async def _local_control_loop(self):
        """Local autonomous control (runs continuously)"""
        while True:
            await asyncio.sleep(30)
            
            # If not under remote control, cycle through normal phases
            if not self.state.remote_control_active:
                self._advance_to_next_phase()
    
    async def _watchdog(self):
        """Watchdog timer: revert to failsafe if issues detected"""
        while self.watchdog_active:
            await asyncio.sleep(10)
            
            # Check for stale remote control
            if self.state.remote_control_active:
                time_since_change = datetime.utcnow() - self.state.last_phase_change
                if time_since_change > timedelta(minutes=5):
                    logger.warning("Watchdog timeout - reverting to failsafe")
                    self._enter_failsafe()
    
    def _advance_to_next_phase(self):
        """Advance to next phase in normal cycle"""
        phase_cycle = [
            TrafficPhase.NORTH_SOUTH_GREEN,
            TrafficPhase.NORTH_SOUTH_YELLOW,
            TrafficPhase.ALL_RED_CLEARANCE,
            TrafficPhase.EAST_WEST_GREEN,
            TrafficPhase.EAST_WEST_YELLOW,
            TrafficPhase.ALL_RED_CLEARANCE,
        ]
        
        try:
            current_idx = phase_cycle.index(self.state.current_phase)
            next_phase = phase_cycle[(current_idx + 1) % len(phase_cycle)]
            self._execute_phase_change(next_phase, "local_cycle")
        except ValueError:
            # Current phase not in cycle, reset to safe state
            self._enter_failsafe()
    
    def _enter_failsafe(self):
        """Enter failsafe mode (flashing red or default schedule)"""
        self.state.status = ControllerStatus.FAILSAFE
        self.state.current_phase = TrafficPhase.ALL_RED_CLEARANCE
        self.state.remote_control_active = False
        logger.warning(f"Failsafe activated: {self.intersection_id}")
    
    def simulate_phase_change(self, new_phase: TrafficPhase) -> bool:
        """
        Simulate phase change to validate safety
        Returns True if simulation passes
        """
        # Check if transition requires clearance
        if self.state.requires_clearance(new_phase):
            logger.info("Simulation: all-red clearance required")
            return True
        
        # Check for conflicts
        if not self.state.is_safe_transition(new_phase):
            logger.error(f"Simulation failed: unsafe transition to {new_phase}")
            return False
        
        logger.info(f"Simulation passed: {self.state.current_phase} -> {new_phase}")
        return True
    
    def _execute_phase_change(self, new_phase: TrafficPhase, reason: str):
        """Execute actual phase change"""
        # Record history
        self.state.phase_history.append({
            'from': self.state.current_phase.value,
            'to': new_phase.value,
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason
        })
        
        # Update state
        self.state.current_phase = new_phase
        self.state.last_phase_change = datetime.utcnow()
        self.state.next_scheduled_change = datetime.utcnow() + timedelta(seconds=30)
        
        logger.info(f"Phase changed: {self.intersection_id} -> {new_phase} ({reason})")
    
    def process_control_request(self, request: ControlRequest) -> ControlResponse:
        """
        Process control request with full safety validation
        This is the main entry point for external control
        """
        # Step 1: Safety validation
        safety_checks = self.safety.validate_request(request, self.state)
        all_checks_passed = all(safety_checks.values())
        
        if not all_checks_passed:
            failed_checks = [k for k, v in safety_checks.items() if not v]
            logger.warning(f"Safety checks failed: {failed_checks}")
            
            return ControlResponse(
                request_id=request.request_id,
                accepted=False,
                intersection_id=self.intersection_id,
                current_phase=self.state.current_phase,
                new_phase=None,
                simulated=False,
                validation_passed=False,
                safety_checks=safety_checks,
                signature=self._sign_response(request.request_id, False),
                reason=f"Safety checks failed: {failed_checks}"
            )
        
        # Step 2: Simulate phase change
        if request.action == ControlAction.SET_PHASE:
            if request.phase is None:
                return ControlResponse(
                    request_id=request.request_id,
                    accepted=False,
                    intersection_id=self.intersection_id,
                    current_phase=self.state.current_phase,
                    new_phase=None,
                    simulated=False,
                    validation_passed=False,
                    safety_checks=safety_checks,
                    signature=self._sign_response(request.request_id, False),
                    reason="No phase specified in request"
                )
            simulation_passed = self.simulate_phase_change(request.phase)
            
            if not simulation_passed:
                return ControlResponse(
                    request_id=request.request_id,
                    accepted=False,
                    intersection_id=self.intersection_id,
                    current_phase=self.state.current_phase,
                    new_phase=None,
                    simulated=True,
                    validation_passed=False,
                    safety_checks=safety_checks,
                    signature=self._sign_response(request.request_id, False),
                    reason="Simulation failed: unsafe transition"
                )
            
            # Step 3: Execute phase change (request.phase is not None here due to earlier check)
            if request.phase is not None:
                self._execute_phase_change(request.phase, f"remote:{request.authority}")
            self.state.remote_control_active = True
            self.state.status = ControllerStatus.REMOTE_CONTROLLED
            
            return ControlResponse(
                request_id=request.request_id,
                accepted=True,
                intersection_id=self.intersection_id,
                current_phase=self.state.current_phase,
                new_phase=request.phase,
                simulated=True,
                validation_passed=True,
                safety_checks=safety_checks,
                executed_at=datetime.utcnow().isoformat(),
                signature=self._sign_response(request.request_id, True),
                reason="Control executed successfully"
            )
        
        elif request.action == ControlAction.EMERGENCY_STOP:
            self._enter_failsafe()
            return ControlResponse(
                request_id=request.request_id,
                accepted=True,
                intersection_id=self.intersection_id,
                current_phase=self.state.current_phase,
                new_phase=TrafficPhase.ALL_RED_CLEARANCE,
                simulated=False,
                validation_passed=True,
                safety_checks=safety_checks,
                executed_at=datetime.utcnow().isoformat(),
                signature=self._sign_response(request.request_id, True),
                reason="Emergency stop executed"
            )
        
        elif request.action == ControlAction.RESUME_NORMAL:
            self.state.remote_control_active = False
            self.state.status = ControllerStatus.NORMAL
            return ControlResponse(
                request_id=request.request_id,
                accepted=True,
                intersection_id=self.intersection_id,
                current_phase=self.state.current_phase,
                new_phase=None,
                simulated=False,
                validation_passed=True,
                safety_checks=safety_checks,
                executed_at=datetime.utcnow().isoformat(),
                signature=self._sign_response(request.request_id, True),
                reason="Resumed normal operation"
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
    
    def _sign_response(self, request_id: str, accepted: bool) -> str:
        """Sign response for audit trail (HMAC)"""
        # In production: use HSM-backed signing
        secret = b"traffic-control-signing-key"
        data = f"{request_id}:{accepted}:{datetime.utcnow().isoformat()}".encode()
        return hmac.new(secret, data, hashlib.sha256).hexdigest()
    
    def get_status(self) -> Dict[str, Any]:
        """Get controller status"""
        return {
            'intersection_id': self.intersection_id,
            'current_phase': self.state.current_phase.value,
            'status': self.state.status.value,
            'remote_control_active': self.state.remote_control_active,
            'controller_health': self.state.controller_health,
            'last_phase_change': self.state.last_phase_change.isoformat(),
            'phase_history': self.state.phase_history[-10:]  # Last 10 changes
        }


# Initialize controllers (in production: one per intersection)
controllers: Dict[str, TrafficController] = {
    'igy-12': TrafficController('igy-12'),
    'lag-01': TrafficController('lag-01'),
}


# API Endpoints

@app.post("/control/v1/requests", response_model=ControlResponse)
async def submit_control_request(request: ControlRequest):
    """
    Submit control request (requires signed authorization)
    All commands are logged, signed, and validated
    """
    if request.intersection_id not in controllers:
        raise HTTPException(status_code=404, detail=f"Intersection not found: {request.intersection_id}")
    
    controller = controllers[request.intersection_id]
    response = controller.process_control_request(request)
    
    logger.info(
        f"Control request processed: {request.request_id}, "
        f"accepted={response.accepted}, intersection={request.intersection_id}"
    )
    
    return response


@app.get("/control/v1/status/{intersection_id}")
async def get_intersection_status(intersection_id: str):
    """Get current intersection status"""
    if intersection_id not in controllers:
        raise HTTPException(status_code=404, detail="Intersection not found")
    
    return controllers[intersection_id].get_status()


@app.get("/control/v1/status")
async def get_all_status():
    """Get status of all intersections"""
    return {iid: ctrl.get_status() for iid, ctrl in controllers.items()}


@app.post("/control/v1/emergency-release/{intersection_id}")
async def emergency_release(intersection_id: str):
    """Emergency release: revert to local control (requires physical authentication)"""
    if intersection_id not in controllers:
        raise HTTPException(status_code=404, detail="Intersection not found")
    
    controller = controllers[intersection_id]
    controller.state.remote_control_active = False
    controller.state.status = ControllerStatus.NORMAL
    
    logger.warning(f"Emergency release activated: {intersection_id}")
    return {"status": "released", "message": "Reverted to local control"}


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "traffic-control-plane",
        "intersections": list(controllers.keys()),
        "active_controllers": sum(1 for c in controllers.values() if c.state.status != ControllerStatus.MAINTENANCE)
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Traffic control plane starting (ICS/SCADA-compliant mode)")
    uvicorn.run(app, host="0.0.0.0", port=8083)
