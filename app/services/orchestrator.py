import asyncio 
from loguru import logger 
 
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, ValidationResult 
from app.services.agents.red_flag import RedFlagAgent 
from app.services.agents.differential import DifferentialAgent 
from app.services.agents.followup import FollowUpAgent 
from app.services.agents.workup import WorkupAgent 
from app.services.agents.stg import STGAgent 
from app.retrieval.hybrid import HybridSearcher 
 
_searcher: HybridSearcher | None = None 
 
def get_searcher() -> HybridSearcher: 
    global _searcher 
    if _searcher is None: 
        _searcher = HybridSearcher() 
    return _searcher 
 
async def run_pipeline(request: AnalyzeRequest) -> AnalyzeResponse: 
    searcher = get_searcher() 
 
    logger.debug('Stage 1: Red Flag Detection') 
    red_flag_agent = RedFlagAgent(searcher) 
    triage = await red_flag_agent.run(request) 
 
    logger.debug('Stage 2: Differential Generation') 
    diff_agent = DifferentialAgent(searcher) 
    differentials = await diff_agent.run(request, triage) 
 
    logger.debug('Stage 3: Parallel agents') 
    followup_agent = FollowUpAgent(searcher) 
    workup_agent = WorkupAgent(searcher) 
    stg_agent = STGAgent(searcher) 
 
    follow_up, workup, treatment = await asyncio.gather( 
        followup_agent.run(request, differentials), 
        workup_agent.run(request, differentials), 
        stg_agent.run(request, differentials), 
        return_exceptions=True, 
    ) 
 
    if isinstance(follow_up, Exception): 
        logger.warning(f'FollowUpAgent failed: {follow_up}') 
        from app.models.schemas import FollowUpResult 
        follow_up = FollowUpResult() 
 
    if isinstance(workup, Exception): 
        logger.warning(f'WorkupAgent failed: {workup}') 
        from app.models.schemas import WorkupResult 
        workup = WorkupResult() 
 
    if isinstance(treatment, Exception): 
        logger.warning(f'STGAgent failed: {treatment}') 
        treatment = None 
 
    return AnalyzeResponse( 
        triage=triage, 
        differentials=differentials, 
        follow_up=follow_up, 
        workup=workup, 
        treatment=treatment, 
        validation=ValidationResult(), 
    ) 
