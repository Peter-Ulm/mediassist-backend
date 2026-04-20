from pydantic import BaseModel, Field 
from typing import List, Optional, Literal 
from enum import Enum 
import uuid 
 
# ÄÄÄ ENUMS ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ 
class TriageLevel(str, Enum): 
    EMERGENCY = 'EMERGENCY' 
    URGENT    = 'URGENT' 
    ROUTINE   = 'ROUTINE' 
 
class Probability(str, Enum): 
    HIGH     = 'high' 
    MODERATE = 'moderate' 
    LOW      = 'low' 
 
# ÄÄÄ REQUEST MODELS ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ 
class PatientData(BaseModel): 
    age: float = Field(..., gt=0, description='Age in years or months') 
    age_unit: Literal['years', 'months'] = 'years' 
    sex: Literal['M', 'F'] 
    weight_kg: Optional[float] = None 
 
class VitalSigns(BaseModel): 
    temperature_c:           Optional[float] = None 
    heart_rate_bpm:          Optional[int]   = None 
    respiratory_rate_bpm:    Optional[int]   = None 
    bp_systolic:             Optional[int]   = None 
    bp_diastolic:            Optional[int]   = None 
    oxygen_saturation_pct:   Optional[float] = None 
    gcs:                     Optional[int]   = None 
 
class PresentationData(BaseModel): 
    chief_complaint: str = Field(..., min_length=3) 
    symptoms: List[str] = Field(..., min_length=1) 
    history_present_illness: Optional[str] = None 
    vital_signs: Optional[VitalSigns] = None 
 
class ResourcesAvailable(BaseModel): 
    lab_available:       bool = False 
    xray_available:      bool = False 
    ultrasound_available:bool = False 
    ct_available:        bool = False 
    lp_kit_available:    bool = False 
 
class ContextData(BaseModel): 
    facility_level: Literal['district', 'regional', 'referral'] = 'district' 
    season: Optional[Literal['dry', 'rainy']] = None 
    malaria_zone: Literal['high', 'moderate', 'low'] = 'high' 
    resources: ResourcesAvailable = ResourcesAvailable() 
 
class AnalyzeRequest(BaseModel): 
    patient:      PatientData 
    presentation: PresentationData 
    context:      ContextData 
 
# ÄÄÄ RESPONSE MODELS ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ 
class DangerSign(BaseModel): 
    sign:         str 
    significance: str 
    source:       str = 'WHO-IMCI' 
 
class TriageResult(BaseModel): 
    level:       TriageLevel 
    danger_signs: List[DangerSign] = [] 
 
class Differential(BaseModel): 
    rank:                  int 
    condition:             str 
    probability:           Probability 
    supporting_evidence:   List[str] 
    contradicting_evidence:List[str] = [] 
    discriminating_test:   str 
 
class FollowUpQuestion(BaseModel): 
    question:              str 
    reasoning:             str 
    targets_differential:  List[str] 
 
class FollowUpResult(BaseModel): 
    history:               List[FollowUpQuestion] = [] 
    exposure:              List[FollowUpQuestion] = [] 
    associated_symptoms:   List[FollowUpQuestion] = [] 
 
class WorkupStep(BaseModel): 
    order:    int 
    action:   str 
    rationale:str 
    urgency:  Literal['stat', 'urgent', 'routine'] 
 
class WorkupResult(BaseModel): 
    with_resources:    List[WorkupStep] = [] 
    without_resources: List[WorkupStep] = [] 
 
class DrugProtocol(BaseModel): 
    drug:             str 
    dose:             str 
    route:            str 
    frequency:        str 
    duration:         str 
    monitoring:       List[str] = [] 
    contraindications:List[str] = [] 
 
class TreatmentResult(BaseModel): 
    working_diagnosis:str 
    protocols:        List[DrugProtocol] = [] 
 
class ValidationResult(BaseModel): 
    gatekeeper_passed:bool = True 
    auditor_passed:   bool = True 
    strategist_passed:bool = True 
    warnings:         List[str] = [] 
    blocked_items:    List[str] = [] 
 
class AnalyzeResponse(BaseModel): 
    request_id:    str = Field(default_factory=lambda: str(uuid.uuid4())) 
    triage:        TriageResult 
    differentials: List[Differential] = [] 
    follow_up:     FollowUpResult     = FollowUpResult() 
    workup:        WorkupResult        = WorkupResult() 
    treatment:     Optional[TreatmentResult] = None 
    validation:    ValidationResult    = ValidationResult() 
