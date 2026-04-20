from abc import ABC, abstractmethod 
from typing import Any 
import httpx, json, re 
from loguru import logger 
from app.config import get_settings 
 
class BaseAgent(ABC): 
    """Abstract base class for all MediAssist agents.""" 
 
    def __init__(self, searcher): 
        self.searcher = searcher 
        self.settings = get_settings() 
 
    async def call_llm(self, prompt: str, system: str = '') -> str: 
        """Call Ollama with the given prompt. Returns raw text.""" 
        payload = { 
            'model': self.settings.ollama_model, 
            'messages': [ 
                {'role': 'system', 'content': system} if system else None, 
                {'role': 'user',   'content': prompt}, 
            ], 
            'stream': False, 
            'format': 'json', 
            'options': {'temperature': 0.1, 'num_predict': 2048}, 
        } 
        payload['messages'] = [m for m in payload['messages'] if m] 
 
        async with httpx.AsyncClient( 
            timeout=self.settings.ollama_timeout 
        ) as client: 
            try: 
                r = await client.post( 
                    f'{self.settings.ollama_url}/api/chat', 
                    json=payload, 
                ) 
                r.raise_for_status() 
                return r.json()['message']['content'] 
            except httpx.ConnectError: 
                raise ConnectionError( 
                    'Cannot connect to Ollama. Run: ollama serve' 
                ) 
 
    def parse_json(self, text: str) -> dict: 
        """Safely parse JSON from LLM output.""" 
        try: 
            return json.loads(text) 
        except json.JSONDecodeError: 
            match = re.search(r'\{.*\}', text, re.DOTALL) 
            if match: 
                return json.loads(match.group()) 
            logger.warning(f'JSON parse failed for: {text[:200]}') 
            return {} 
 
    @abstractmethod 
    async def run(self, *args, **kwargs) -> Any: 
        """Run the agent.""" 
        ... 
