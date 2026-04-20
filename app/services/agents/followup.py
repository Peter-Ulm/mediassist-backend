from app.services.agents.base_agent import BaseAgent 
from app.models.schemas import ( 
    AnalyzeRequest, Differential, FollowUpResult, FollowUpQuestion 
) 
 
SYSTEM = 'You are a clinical educator generating follow-up questions.' 
 
class FollowUpAgent(BaseAgent): 
    """Agent 3: Generates targeted follow-up questions.""" 
 
    async def run( 
        self, request: AnalyzeRequest, differentials: list[Differential] 
    ) -> FollowUpResult: 
 
        top3 = [d.condition for d in differentials[:3]] 
 
        prompt = f'''Generate follow-up questions to discriminate between: 
{', '.join(top3)} 
 
CURRENT SYMPTOMS: {', '.join(request.presentation.symptoms)} 
 
Generate 3 questions per category: history, exposure, associated_symptoms. 
Return JSON: 
{{ 
  "history": [{{"question":"..","reasoning":"..","targets_differential":[".."]}}], 
  "exposure": [...], 
  "associated_symptoms": [...] 
}} 
''' 
 
        raw = await self.call_llm(prompt, SYSTEM) 
        data = self.parse_json(raw) 
 
        def parse_qs(key): 
            return [ 
                FollowUpQuestion( 
                    question=q.get('question',''), 
                    reasoning=q.get('reasoning',''), 
                    targets_differential=q.get('targets_differential',[]), 
                ) 
                for q in data.get(key, []) 
                if isinstance(q, dict) 
            ] 
 
        return FollowUpResult( 
            history=parse_qs('history'), 
            exposure=parse_qs('exposure'), 
            associated_symptoms=parse_qs('associated_symptoms'), 
        ) 
