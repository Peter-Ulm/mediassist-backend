from app.services.agents.base_agent import BaseAgent 
from app.models.schemas import ( 
    AnalyzeRequest, Differential, WorkupResult, WorkupStep 
) 
 
SYSTEM = 'You are a resource-aware clinical planner in Tanzania.' 
 
class WorkupAgent(BaseAgent): 
    """Agent 4: Generates resource-aware workup plans.""" 
 
    async def run( 
        self, request: AnalyzeRequest, differentials: list[Differential] 
    ) -> WorkupResult: 
 
        res = request.context.resources 
        resources_str = (f'Lab:{res.lab_available}, X-ray:{res.xray_available}, ' 
                         f'US:{res.ultrasound_available}, CT:{res.ct_available}') 
        top3 = [d.condition for d in differentials[:3]] 
 
        prompt = f'''Create workup plan for top differentials: {', '.join(top3)} 
 
FACILITY: {request.context.facility_level} 
RESOURCES: {resources_str} 
 
Return JSON with two plans - one WITH resources, one WITHOUT: 
{{ 
  "with_resources": [{{"order":1,"action":"..","rationale":"..","urgency":"stat|urgent|routine"}}], 
  "without_resources": [...] 
}} 
''' 
 
        raw = await self.call_llm(prompt, SYSTEM) 
        data = self.parse_json(raw) 
 
        def parse_steps(key): 
            return [ 
                WorkupStep( 
                    order=s.get('order', i+1), 
                    action=s.get('action', ''), 
                    rationale=s.get('rationale', ''), 
                    urgency=s.get('urgency', 'routine'), 
                ) 
                for i, s in enumerate(data.get(key, [])) 
                if isinstance(s, dict) 
            ] 
 
        return WorkupResult( 
            with_resources=parse_steps('with_resources'), 
            without_resources=parse_steps('without_resources'), 
        ) 
