import aiohttp
import json
import logging
import os
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.3")

    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        context: Optional[List[int]] = None
    ) -> Dict:
        """
        Generate a response from Ollama.
        Pitfall 2: LLM Financial Hallucinations - Prompting should emphasize accuracy.
        """
        url = f"{self.ollama_host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if context:
            payload["context"] = context

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama error: {response.status} - {error_text}")
                        return {"error": f"Ollama error: {response.status}", "response": "I'm having trouble connecting to my brain right now."}
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return {"error": str(e), "response": "Ollama is not reachable. Is it running?"}

    async def analyze_market(self, market_data: Dict) -> str:
        system_prompt = (
            "You are an expert trading analyst and coach. "
            "Analyze the provided market data and explain price movements in plain language. "
            "Be concise and actionable. If you don't have enough data, say so. "
            "IMPORTANT: Do not hallucinate numbers. Only use the data provided."
        )
        
        prompt = f"Current Market Data: {json.dumps(market_data)}\n\nExplain what's happening."
        
        result = await self.generate_response(prompt, system_prompt=system_prompt)
        return result.get("response", "Could not generate analysis.")

llm_engine = LLMEngine()
