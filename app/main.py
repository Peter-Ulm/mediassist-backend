from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse 
from contextlib import asynccontextmanager 
from loguru import logger 
import time 
 
from app.config import get_settings 
from app.routers import analyze, health 
 
settings = get_settings() 
 
@asynccontextmanager 
async def lifespan(app: FastAPI): 
    logger.info('MediAssist v4 starting up...') 
    logger.info(f'Ollama URL: {settings.ollama_url}') 
    logger.info(f'Model: {settings.ollama_model}') 
    yield 
    logger.info('MediAssist v4 shutting down...') 
 
app = FastAPI( 
    title='MediAssist v4 API', 
    description='Clinical Decision Support System', 
    version='4.0.0', 
    lifespan=lifespan, 
    docs_url='/docs', 
    redoc_url='/redoc', 
) 
 
app.add_middleware( 
    CORSMiddleware, 
    allow_origins=settings.cors_origins_list, 
    allow_credentials=True, 
    allow_methods=['*'], 
    allow_headers=['*'], 
) 
 
@app.middleware('http') 
async def add_timing_header(request: Request, call_next): 
    start = time.time() 
    response = await call_next(request) 
    elapsed = round((time.time() - start) * 1000) 
    response.headers['X-Process-Time-Ms'] = str(elapsed) 
    logger.debug(f'{request.method} {request.url.path}  {response.status_code} ({elapsed}ms)') 
    return response 
 
@app.exception_handler(Exception) 
async def global_exception_handler(request: Request, exc: Exception): 
    logger.error(f'Unhandled exception: {exc}', exc_info=True) 
    return JSONResponse( 
        status_code=500, 
        content={'detail': 'Internal server error. Check logs.'}, 
    ) 
 
app.include_router(health.router, prefix='/api/v1', tags=['Health']) 
app.include_router(analyze.router, prefix='/api/v1', tags=['Analysis']) 
