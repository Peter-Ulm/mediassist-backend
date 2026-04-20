from pydantic_settings import BaseSettings 
from functools import lru_cache 
 
class Settings(BaseSettings): 
    environment: str = 'development' 
    log_level: str = 'DEBUG' 
    ollama_url: str = 'http://localhost:11434' 
    ollama_model: str = 'mistral:7b-instruct' 
    ollama_timeout: int = 60 
    database_url: str = 'sqlite+aiosqlite:///./data/sqlite/mediassist.db' 
    chroma_persist_dir: str = './data/chroma' 
    chroma_collection: str = 'mediassist_kb' 
    cors_origins: str = 'http://localhost:3000' 
    secret_key: str = 'dev-secret-key' 
 
    @property 
    def cors_origins_list(self) -> list[str]: 
        return [o.strip() for o in self.cors_origins.split(',')] 
 
    class Config: 
        env_file = '.env' 
 
@lru_cache() 
def get_settings() -> Settings: 
    return Settings() 
