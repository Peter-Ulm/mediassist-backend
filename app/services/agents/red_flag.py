from app.services.agents.base_agent import BaseAgent 
from app.models.schemas import ( 
    AnalyzeRequest, TriageResult, TriageLevel, DangerSign 
) 
from loguru import logger 
 
SYSTEM = '''You are a clinical triage specialist. 
Analyze the patient for danger signs per WHO IMCI guidelines. 
Always output valid JSON. Be conservative - when in doubt, escalate. 
''' 
 
class RedFlagAgent(BaseAgent): 
    """Agent 1: Detects danger signs and assigns triage level.""" 
 
    async def run(self, request: AnalyzeRequest) -> TriageResult: 
        vitals = request.presentation.vital_signs 
        vitals_str = '' 
        if vitals: 
            vitals_str = ( 
                f'Temp: {vitals.temperature_c}øC, ' 
                f'HR: {vitals.heart_rate_bpm}bpm, ' 
                f'RR: {vitals.respiratory_rate_bpm}/min, ' 
                f'SpO2: {vitals.oxygen_saturation_pct}%, ' 
                f'GCS: {vitals.gcs}' 
            ) 
 
        prompt = f'''Analyze this patient for danger signs: 
 
PATIENT: {request.patient.age} {request.patient.age_unit}, {request.patient.sex} 
CHIEF COMPLAINT: {request.presentation.chief_complaint} 
SYMPTOMS: {', '.join(request.presentation.symptoms)} 
VITALS: {vitals_str or 'Not recorded'} 
MALARIA ZONE: {request.context.malaria_zone} 
 
Identify ALL danger signs present. Determine triage level. 
TRIAGE RULES: 
- EMERGENCY: airway/breathing/circulation compromise, GCS<9, active seizure, shock 
- URGENT: abnormal vitals, GCS 9-13, severe pain, danger signs present 
- ROUTINE: stable, no immediate threat 
 
Return JSON in this exact format: 
{{ 
  "triage_level": "EMERGENCY|URGENT|ROUTINE", 
  "danger_signs": [ 
    {{"sign": "...", "significance": "...", "source": "WHO-IMCI"}} 
  ] 
}} 
''' 
 
        raw = await self.call_llm(prompt, SYSTEM) 
        data = self.parse_json(raw) 
 
        level_str = data.get('triage_level', 'ROUTINE') 
        try: 
            level = TriageLevel(level_str) 
        except ValueError: 
            level = TriageLevel.ROUTINE 
 
        signs = [ 
            DangerSign(**s) for s in data.get('danger_signs', []) 
            if isinstance(s, dict) and 'sign' in s 
        ] 
 
        logger.info(f'Red Flag: {level.value}, {len(signs)} danger signs') 
        return TriageResult(level=level, danger_signs=signs) 
