from fastapi import APIRouter, HTTPException 
from loguru import logger 
 
from app.models.schemas import AnalyzeRequest, AnalyzeResponse 
from app.services.orchestrator import run_pipeline 
 
router = APIRouter() 
 
@router.post('/analyze', response_model=AnalyzeResponse) 
async def analyze_case(request: AnalyzeRequest) -> AnalyzeResponse: 
    logger.info(f'Analyzing case: {request.presentation.chief_complaint}') 
 
    try: 
        result = await run_pipeline(request) 
        logger.info(f'Analysis complete. Triage: {result.triage.level}') 
        return result 
    except ConnectionError as e: 
        logger.error(f'Ollama connection failed: {e}') 
        raise HTTPException(status_code=503, detail='AI service unavailable. Ensure Ollama is running: ollama serve') 
    except Exception as e: 
        logger.error(f'Pipeline error: {e}', exc_info=True) 
        raise HTTPException(status_code=500, detail=str(e)) 
