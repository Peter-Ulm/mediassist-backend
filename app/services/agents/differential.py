from app.services.agents.base_agent import BaseAgent 
from app.models.schemas import ( 
    AnalyzeRequest, TriageResult, Differential, Probability 
) 
from loguru import logger 
 
SYSTEM = '''You are a clinical diagnostician in Tanzania. 
Generate ranked differentials considering local epidemiology. 
Always output valid JSON with exact field names specified. 
''' 
 
class DifferentialAgent(BaseAgent): 
    """Agent 2: Generates ranked differential diagnosis list.""" 
 
    async def run( 
        self, request: AnalyzeRequest, triage: TriageResult 
    ) -> list[Differential]: 
 
        danger_text = ', '.join(s.sign for s in triage.danger_signs) or 'None' 
 
        prompt = f'''Generate differential diagnosis for: 
 
PATIENT: {request.patient.age} {request.patient.age_unit}, {request.patient.sex} 
CHIEF COMPLAINT: {request.presentation.chief_complaint} 
SYMPTOMS: {', '.join(request.presentation.symptoms)} 
TRIAGE LEVEL: {triage.level.value} 
DANGER SIGNS: {danger_text} 
MALARIA ZONE: {request.context.malaria_zone} 
SEASON: {request.context.season or 'unknown'} 
FACILITY: {request.context.facility_level} 
 
Generate 3-5 ranked differentials. Consider local epidemiology. 
In high malaria zones + rainy season: malaria must be in top 3 for febrile illness. 
 
Return JSON: 
{{ 
  "differentials": [ 
    {{ 
      "rank": 1, 
      "condition": "Condition Name", 
      "probability": "high|moderate|low", 
      "supporting_evidence": ["finding 1", "finding 2"], 
      "contradicting_evidence": ["doesn't fit"], 
      "discriminating_test": "specific test" 
    }} 
  ] 
}} 
''' 
 
        raw = await self.call_llm(prompt, SYSTEM) 
        data = self.parse_json(raw) 
 
        results = [] 
        for item in data.get('differentials', [])[:5]: 
            try: 
                prob = Probability(item.get('probability', 'low')) 
            except ValueError: 
                prob = Probability.LOW 
 
            results.append(Differential( 
                rank=item.get('rank', len(results)+1), 
                condition=item.get('condition', 'Unknown'), 
                probability=prob, 
                supporting_evidence=item.get('supporting_evidence', []), 
                contradicting_evidence=item.get('contradicting_evidence', []), 
                discriminating_test=item.get('discriminating_test', 'Clinical evaluation'), 
            )) 
 
        logger.info(f'Differentials: {[d.condition for d in results]}') 
        return results 
