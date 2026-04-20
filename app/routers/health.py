from fastapi import APIRouter 
from app.config import get_settings 
import httpx 
 
router = APIRouter() 
 
@router.get('/health') 
async def health_check(): 
    settings = get_settings() 
    ollama_ok = False 
    try: 
        async with httpx.AsyncClient(timeout=5) as client: 
            r = await client.get(f'{settings.ollama_url}/api/tags') 
            ollama_ok = r.status_code == 200 
    except Exception: 
        pass 
 
    return { 
        'status': 'healthy' if ollama_ok else 'degraded', 
        'api': 'ok', 
        'ollama': 'ok' if ollama_ok else 'unavailable', 
        'model': settings.ollama_model, 
    } 
