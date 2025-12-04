/**
 * API Service for National Security Platform
 * Connects all dashboard pages to backend services
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  timestamp?: string;
}

// ============================================================================
// NATIONAL OVERVIEW
// ============================================================================

export interface NationalOverview {
  national_security_overview: {
    threat_level: string;
    last_updated: string;
    active_incidents: number;
    systems_operational: number;
    systems_degraded: number;
    systems_offline: number;
  };
  infrastructure: {
    pipelines_monitored: number;
    pipelines_healthy: number;
    active_leak_alerts: number;
    radiation_sensors: number;
    radiation_alerts: number;
  };
  transportation: {
    trains_tracked: number;
    trains_on_schedule: number;
    trains_delayed: number;
    cctv_cameras: number;
    threat_detections_24h: number;
    passenger_safety_incidents: number;
  };
  law_enforcement: {
    officers_on_duty: number;
    highway_patrol_units: number;
    active_incidents: number;
    emergency_responses_24h: number;
    average_response_time_minutes: number;
  };
  immigration: {
    airport_terminals: number;
    officers_on_duty: number;
    passengers_processed_24h: number;
    passport_applications_pending: number;
    high_risk_passengers_flagged: number;
  };
  media_monitoring: {
    sources_monitored: number;
    content_verified_24h: number;
    misinformation_detected: number;
    emergency_alerts_active: number;
  };
  citizen_services: {
    active_citizens: number;
    service_requests_24h: number;
    service_requests_processed: number;
    approval_rate_percent: number;
  };
}

export async function getNationalOverview(): Promise<ApiResponse<NationalOverview>> {
  try {
    const response = await fetch(`${API_BASE_URL}/overview/national`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch national overview' };
  }
}

// ============================================================================
// PIPELINE INFRASTRUCTURE MONITORING
// ============================================================================

export interface PipelineStatistics {
  pipeline_infrastructure: {
    total_pipelines: number;
    pipelines_monitored: number;
    total_length_km: number;
    monitoring_coverage_percent: number;
  };
  leak_detection: {
    active_leaks: number;
    leaks_detected_period: number;
    leaks_repaired: number;
    false_positive_rate: number;
    average_detection_time_minutes: number;
  };
  radiation_monitoring: {
    sensors_active: number;
    sensors_total: number;
    radiation_alerts: number;
    average_background_level: number;
    threshold_level: number;
  };
  predictive_maintenance: {
    pipelines_requiring_maintenance: number;
    maintenance_scheduled: number;
    predicted_failures_prevented: number;
    cost_savings_estimate: number;
  };
  environmental_impact: {
    spills_prevented: number;
    environmental_incidents: number;
    cleanup_operations_active: number;
  };
}

export async function getPipelineStatistics(timerange = '24h'): Promise<ApiResponse<PipelineStatistics>> {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/statistics?timerange=${timerange}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch pipeline statistics' };
  }
}

// ============================================================================
// RAILWAY SECURITY & CCTV MONITORING
// ============================================================================

export interface RailwayStatistics {
  train_operations: {
    trains_tracked: number;
    trains_on_schedule: number;
    trains_delayed: number;
    average_delay_minutes: number;
    on_time_performance_percent: number;
  };
  cctv_monitoring: {
    cameras_total: number;
    cameras_operational: number;
    coverage_percent: number;
    ai_analysis_enabled: number;
    threat_detections: number;
  };
  passenger_safety: {
    passengers_monitored_period: number;
    safety_incidents: number;
    crowd_warnings: number;
    emergency_responses: number;
  };
  station_security: {
    stations_monitored: number;
    security_officers: number;
    access_control_points: number;
    security_breaches: number;
  };
  threat_detection: {
    suspicious_activities_flagged: number;
    threats_confirmed: number;
    false_positive_rate: number;
    average_response_time_seconds: number;
  };
}

export async function getRailwayStatistics(timerange = '24h'): Promise<ApiResponse<RailwayStatistics>> {
  try {
    const response = await fetch(`${API_BASE_URL}/railway/statistics?timerange=${timerange}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch railway statistics' };
  }
}

// ============================================================================
// LAW ENFORCEMENT & POLICE OPERATIONS
// ============================================================================

export interface PoliceStatistics {
  officer_deployment: {
    total_officers: number;
    officers_on_duty: number;
    officers_available: number;
    officers_on_call: number;
    utilization_rate_percent: number;
  };
  highway_patrol: {
    patrol_units: number;
    units_active: number;
    highways_covered: number;
    traffic_stops: number;
    citations_issued: number;
    accidents_responded: number;
  };
  incident_management: {
    active_incidents: number;
    incidents_period: number;
    incidents_resolved: number;
    average_response_time_minutes: number;
    emergency_incidents: number;
  };
  performance_metrics: {
    clearance_rate_percent: number;
    citizen_satisfaction_percent: number;
    officer_safety_incidents: number;
  };
}

export async function getPoliceStatistics(state?: string, timerange = '24h'): Promise<ApiResponse<PoliceStatistics>> {
  try {
    const params = new URLSearchParams({ timerange });
    if (state) params.append('state', state);
    const response = await fetch(`${API_BASE_URL}/police/statistics?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch police statistics' };
  }
}

// ============================================================================
// IMMIGRATION & AIRPORT SECURITY
// ============================================================================

export interface ImmigrationStatistics {
  airport_operations: {
    terminals_monitored: number;
    terminals_operational: number;
    airports_covered: number;
    countries_connected: number;
  };
  passenger_processing: {
    passengers_processed_period: number;
    average_processing_time_minutes: number;
    fast_track_usage_percent: number;
    queue_time_average_minutes: number;
  };
  passport_validation: {
    passports_validated: number;
    validation_success_rate: number;
    expired_passports: number;
    stolen_passports_detected: number;
    forgeries_detected: number;
  };
  biometric_verification: {
    biometric_checks_performed: number;
    verification_success_rate: number;
    manual_reviews_required: number;
    fraud_attempts_detected: number;
  };
  risk_assessment: {
    high_risk_passengers: number;
    watchlist_matches: number;
    secondary_screenings: number;
    denied_entries: number;
  };
  customs_inspection: {
    inspections_performed: number;
    contraband_seizures: number;
    duty_collected_usd: number;
  };
  officer_management: {
    immigration_officers: number;
    officers_on_duty: number;
    customs_officers: number;
    officer_utilization_percent: number;
  };
}

export async function getImmigrationStatistics(airport?: string, timerange = '24h'): Promise<ApiResponse<ImmigrationStatistics>> {
  try {
    const params = new URLSearchParams({ timerange });
    if (airport) params.append('airport', airport);
    const response = await fetch(`${API_BASE_URL}/immigration/statistics?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch immigration statistics' };
  }
}

// ============================================================================
// PASSPORT APPLICATION STATISTICS
// ============================================================================

export interface PassportStatistics {
  passport_applications: {
    total_applications: number;
    applications_submitted_period: number;
    applications_processed: number;
    applications_pending: number;
    processing_rate_percent: number;
  };
  application_status: {
    approved: number;
    approved_percent: number;
    rejected: number;
    rejected_percent: number;
    under_review: number;
    under_review_percent: number;
    pending_documents: number;
  };
  processing_times: {
    average_processing_days: number;
    fastest_processing_days: number;
    slowest_processing_days: number;
    standard_service_days: number;
    expedited_service_days: number;
  };
  application_types: {
    new_passport: number;
    renewal: number;
    replacement: number;
    emergency_travel: number;
  };
  demographics: {
    applications_by_age: Record<string, number>;
    applications_by_state: Record<string, number>;
  };
  rejection_reasons: {
    incomplete_documentation: number;
    invalid_documents: number;
    security_concerns: number;
    payment_issues: number;
    other: number;
  };
  citizen_satisfaction: {
    rating_average: number;
    ratings_count: number;
    complaints_received: number;
    complaints_resolved: number;
  };
}

export async function getPassportStatistics(status?: string, timerange = '30d'): Promise<ApiResponse<PassportStatistics>> {
  try {
    const params = new URLSearchParams({ timerange });
    if (status) params.append('status', status);
    const response = await fetch(`${API_BASE_URL}/immigration/passport-statistics?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch passport statistics' };
  }
}

// ============================================================================
// MEDIA MONITORING
// ============================================================================

export interface MediaStatistics {
  media_monitoring: {
    sources_monitored: number;
    radio_stations: number;
    tv_channels: number;
    online_sources: number;
    sources_active: number;
  };
  content_analysis: {
    content_items_processed: number;
    news_items: number;
    emergency_alerts: number;
    public_announcements: number;
    entertainment: number;
  };
  verification_results: {
    verified_content: number;
    unverified_content: number;
    disputed_content: number;
    false_content: number;
    verification_rate_percent: number;
  };
  misinformation_detection: {
    misinformation_detected: number;
    disinformation_campaigns: number;
    fact_checks_performed: number;
    corrections_issued: number;
  };
  emergency_broadcasting: {
    emergency_alerts_broadcast: number;
    public_safety_announcements: number;
    broadcast_channels_used: number;
    population_reached_estimate: number;
  };
  threat_detection: {
    security_threats_detected: number;
    threat_level: string;
    alerts_generated: number;
    investigations_initiated: number;
  };
}

export async function getMediaStatistics(sourceType?: string, timerange = '24h'): Promise<ApiResponse<MediaStatistics>> {
  try {
    const params = new URLSearchParams({ timerange });
    if (sourceType) params.append('source_type', sourceType);
    const response = await fetch(`${API_BASE_URL}/media/statistics?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch media statistics' };
  }
}

// ============================================================================
// CITIZEN SERVICES
// ============================================================================

export interface CitizenStatistics {
  citizen_accounts: {
    total_citizens: number;
    active_citizens: number;
    verified_citizens: number;
    biometric_enrolled: number;
  };
  service_requests: {
    requests_submitted_period: number;
    requests_processed: number;
    requests_approved: number;
    requests_rejected: number;
    requests_pending: number;
    approval_rate_percent: number;
  };
  service_types: {
    passport_applications: number;
    drivers_licenses: number;
    voter_registration: number;
    birth_certificates: number;
    business_licenses: number;
    other: number;
  };
  processing_performance: {
    average_processing_time_days: number;
    on_time_completion_percent: number;
    sla_compliance_percent: number;
  };
  government_offices: {
    total_offices: number;
    offices_operational: number;
    total_staff: number;
    staff_on_duty: number;
    office_utilization_percent: number;
  };
  digital_services: {
    online_applications: number;
    in_person_applications: number;
    digital_adoption_percent: number;
    mobile_app_users: number;
  };
  citizen_satisfaction: {
    satisfaction_rating: number;
    ratings_count: number;
    complaints_received: number;
    complaints_resolved: number;
    resolution_rate_percent: number;
  };
}

export async function getCitizenStatistics(serviceType?: string, timerange = '24h'): Promise<ApiResponse<CitizenStatistics>> {
  try {
    const params = new URLSearchParams({ timerange });
    if (serviceType) params.append('service_type', serviceType);
    const response = await fetch(`${API_BASE_URL}/citizen/statistics?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch citizen statistics' };
  }
}

// ============================================================================
// THREAT LEVEL
// ============================================================================

export interface ThreatLevel {
  current_level?: string;
  national_threat_level?: {
    current_level: string;
    last_updated: string;
    last_changed: string;
    trend: string;
  };
  threat_indicators?: {
    cyber_threats: string;
    physical_security: string;
    terrorism: string;
    organized_crime: string;
    infrastructure: string;
    public_health: string;
  };
  active_threats?: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  recent_incidents?: {
    past_24h: number;
    past_7d: number;
    past_30d: number;
  };
  recommended_actions?: string[];
}

export async function getThreatLevel(): Promise<ApiResponse<ThreatLevel>> {
  try {
    const response = await fetch(`${API_BASE_URL}/threat-level`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch threat level' };
  }
}

// ============================================================================
// OFFICER STATISTICS
// ============================================================================

export interface OfficerStatistics {
  officer_overview: {
    total_officers: number;
    on_duty: number;
    off_duty: number;
    on_break: number;
    on_leave: number;
    utilization_rate_percent: number;
  };
  by_department: {
    police: {
      total: number;
      on_duty: number;
      available: number;
      on_call: number;
    };
    immigration: {
      total: number;
      on_duty: number;
      airport_security: number;
      customs: number;
    };
    railway_security: {
      total: number;
      on_duty: number;
      station_security: number;
      mobile_patrol: number;
    };
    infrastructure_security: {
      total: number;
      on_duty: number;
      pipeline_monitoring: number;
      emergency_response: number;
    };
    other: {
      total: number;
      on_duty: number;
    };
  };
  by_state: Record<string, number>;
  performance_metrics: {
    average_response_time_minutes: number;
    incidents_handled_24h: number;
    officer_safety_incidents: number;
    training_completion_percent: number;
  };
  shift_management: {
    current_shift: string;
    shift_coverage_percent: number;
    overtime_hours_week: number;
    understaffed_locations: number;
  };
}

export async function getOfficerStatistics(department?: string, state?: string, status?: string): Promise<ApiResponse<OfficerStatistics>> {
  try {
    const params = new URLSearchParams();
    if (department) params.append('department', department);
    if (state) params.append('state', state);
    if (status) params.append('status', status);
    const response = await fetch(`${API_BASE_URL}/personnel/officers?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch officer statistics' };
  }
}

// ============================================================================
// REAL-TIME MONITORING
// ============================================================================

export interface RealtimeMonitoring {
  system_status: {
    all_systems: string;
    last_updated: string;
    update_frequency_seconds: number;
  };
  active_alerts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  live_metrics: {
    pipeline_sensors_active: number;
    cctv_cameras_streaming: number;
    police_units_deployed: number;
    passengers_in_processing: number;
    media_sources_streaming: number;
    citizen_sessions_active: number;
  };
  recent_events: Array<{
    timestamp: string;
    system: string;
    event_type: string;
    severity: string;
    description: string;
    status: string;
  }>;
  performance: {
    api_response_time_ms: number;
    data_freshness_seconds: number;
    system_load_percent: number;
    database_queries_per_second: number;
  };
}

export async function getRealtimeMonitoring(): Promise<ApiResponse<RealtimeMonitoring>> {
  try {
    const response = await fetch(`${API_BASE_URL}/monitoring/real-time`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch real-time monitoring' };
  }
}

// ============================================================================
// DAILY REPORT
// ============================================================================

export interface DailyReport {
  report_metadata: {
    report_type: string;
    report_date: string;
    generated_at: string;
    classification: string;
  };
  executive_summary: {
    overall_status: string;
    threat_level: string;
    major_incidents: number;
    systems_operational: number;
    officer_deployment: string;
  };
  infrastructure_summary: {
    pipelines_monitored: number;
    leaks_detected: number;
    leaks_resolved: number;
    radiation_alerts: number;
  };
  transportation_summary: {
    trains_operated: number;
    on_time_performance: number;
    safety_incidents: number;
    passengers_transported: number;
  };
  law_enforcement_summary: {
    incidents_handled: number;
    arrests_made: number;
    citations_issued: number;
    emergency_responses: number;
  };
  immigration_summary: {
    passengers_processed: number;
    high_risk_flagged: number;
    denied_entries: number;
    passports_validated: number;
  };
  media_summary: {
    content_monitored: number;
    misinformation_detected: number;
    emergency_broadcasts: number;
  };
  citizen_services_summary: {
    requests_processed: number;
    services_completed: number;
    citizen_satisfaction: number;
  };
  recommendations: string[];
}

export async function getDailyReport(date?: string): Promise<ApiResponse<DailyReport>> {
  try {
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    const response = await fetch(`${API_BASE_URL}/reports/daily?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch daily report' };
  }
}

// ============================================================================
// VISA VERIFICATION
// ============================================================================

export interface VisaVerificationRequest {
  visaNumber: string;
  passportNumber: string;
  country?: string;
}

export interface VisaVerificationResult {
  status: string;
  visa_number: string;
  passport_number: string;
  valid: boolean;
  visa_details?: {
    visa_type: string;
    country_of_issue: string;
    issue_date: string;
    expiry_date: string;
    status: string;
    entries_allowed: number | string;
    entries_used: number;
    duration_of_stay_days: number;
  };
  warnings?: (string | null)[];
  restrictions?: (string | null)[];
  verification_details?: {
    verified_at: string;
    verification_method: string;
    confidence_score: number;
  };
  message?: string;
  timestamp: string;
}

export async function verifyVisa(request: VisaVerificationRequest): Promise<ApiResponse<VisaVerificationResult>> {
  try {
    const params = new URLSearchParams({
      visa_number: request.visaNumber,
      passport_number: request.passportNumber,
    });
    if (request.country) {
      params.append('country', request.country);
    }

    const response = await fetch(`${API_BASE_URL}/visa/verify?${params}`, {
      method: 'POST',
    });
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to verify visa' };
  }
}

// ============================================================================
// VISA STATISTICS
// ============================================================================

export interface VisaStatistics {
  visa_issuance: {
    total_visas_issued: number;
    visas_issued_period: number;
    visas_active: number;
    visas_expired: number;
    visas_cancelled: number;
    issuance_rate_change_percent: number;
  };
  visa_types: {
    tourist: number;
    business: number;
    student: number;
    work: number;
    diplomatic: number;
    other: number;
  };
  verification_metrics: {
    verifications_performed: number;
    verifications_period: number;
    valid_visas_confirmed: number;
    invalid_visas_detected: number;
    expired_visas_detected: number;
    fraudulent_visas_detected: number;
    verification_success_rate_percent: number;
  };
  processing_times: {
    average_verification_seconds: number;
    average_issuance_days: number;
    expedited_processing_days: number;
    standard_processing_days: number;
  };
  countries_of_origin: Record<string, number>;
  entry_statistics: {
    entries_with_valid_visa: number;
    entries_rejected_invalid_visa: number;
    visa_overstays_detected: number;
    visa_violations: number;
  };
  security_alerts: {
    high_risk_visas_flagged: number;
    watchlist_matches: number;
    security_reviews_initiated: number;
    visas_revoked_security: number;
  };
  visa_type_filter?: string | null;
  status_filter?: string | null;
  timerange: string;
  timestamp: string;
}

export async function getVisaStatistics(
  visaType?: string,
  status?: string,
  timerange: string = '30d'
): Promise<ApiResponse<VisaStatistics>> {
  try {
    const params = new URLSearchParams({ timerange });
    if (visaType) params.append('visa_type', visaType);
    if (status) params.append('status', status);

    const response = await fetch(`${API_BASE_URL}/immigration/visa-statistics?${params}`);
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch visa statistics' };
  }
}

// ============================================================================
// HEALTH CHECK
// ============================================================================

export interface HealthCheck {
  status: string;
  timestamp: string;
  systems: {
    pipeline_monitoring: string;
    railway_security: string;
    police_operations: string;
    immigration_control: string;
    media_monitoring: string;
    citizen_services: string;
  };
}

export async function getHealthCheck(): Promise<ApiResponse<HealthCheck>> {
  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to fetch health status' };
  }
}

// Export all functions
export default {
  getNationalOverview,
  getPipelineStatistics,
  getRailwayStatistics,
  getPoliceStatistics,
  getImmigrationStatistics,
  getPassportStatistics,
  verifyVisa,
  getVisaStatistics,
  getMediaStatistics,
  getCitizenStatistics,
  getThreatLevel,
  getOfficerStatistics,
  getRealtimeMonitoring,
  getDailyReport,
  getHealthCheck,
};
