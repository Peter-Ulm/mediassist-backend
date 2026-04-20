from app.services.agents.base_agent import BaseAgent 
from app.models.schemas import ( 
    AnalyzeRequest, Differential, TreatmentResult, DrugProtocol 
) 
 
SYSTEM = 'You are an STG pharmacist for Tanzania. Only recommend evidence-based protocols.' 
 
class STGAgent(BaseAgent): 
    """Agent 5: Retrieves STG treatment protocol for top diagnosis.""" 
 
    async def run( 
        self, request: AnalyzeRequest, differentials: list[Differential] 
    ) -> TreatmentResult: 
 
        if not differentials: 
            return TreatmentResult(working_diagnosis='Unknown', protocols=[]) 
 
        top = differentials[0] 
 
        prompt = f'''Provide Tanzania STG treatment protocol for: 
 
DIAGNOSIS: {top.condition} 
PATIENT: {request.patient.age} {request.patient.age_unit}, {request.patient.sex} 
WEIGHT: {request.patient.weight_kg or 'unknown'} kg 
FACILITY: {request.context.facility_level} 
 
Return JSON with treatment protocols: 
{{ 
  "working_diagnosis": "{top.condition}", 
  "protocols": [ 
    {{ 
      "drug": "Drug Name", 
      "dose": "Specific dose with weight-based if pediatric", 
      "route": "oral|IV|IM|SC", 
      "frequency": "frequency", 
      "duration": "duration", 
      "monitoring": ["parameter to monitor"], 
      "contraindications": ["contraindication"] 
    }} 
  ] 
}} 
''' 
 
        raw = await self.call_llm(prompt, SYSTEM) 
        data = self.parse_json(raw) 
 
        protocols = [ 
            DrugProtocol(**p) 
            for p in data.get('protocols', []) 
            if isinstance(p, dict) and 'drug' in p 
        ] 
 
        return TreatmentResult( 
            working_diagnosis=data.get('working_diagnosis', top.condition), 
            protocols=protocols, 
        ) 
