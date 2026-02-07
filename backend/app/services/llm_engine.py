import aiohttp
import json
import logging
import os
from typing import Optional, Dict, List
<<<<<<< HEAD

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.3")
=======
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.mistral_base_url = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
        self.model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self.compliance_footer = (
            "Educational only - not financial advice. "
            "AI-generated content."
        )
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        context: Optional[List[int]] = None
    ) -> Dict:
        """
<<<<<<< HEAD
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
=======
        Generate a response from Mistral.
        Pitfall 2: LLM Financial Hallucinations - Prompting should emphasize accuracy.
        """
        if not self.mistral_api_key:
            logger.error("MISTRAL_API_KEY not found in environment")
            return {
                "error": "missing_api_key",
                "response": "Mistral API key is missing. Please set MISTRAL_API_KEY.",
            }

        url = f"{self.mistral_base_url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Authorization": f"Bearer {self.mistral_api_key}"},
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = (
                            data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "")
                        )
                        return {"response": content}
                    else:
                        error_text = await response.text()
                        logger.error(f"Mistral error: {response.status} - {error_text}")
                        return {
                            "error": f"Mistral error: {response.status}",
                            "response": "I'm having trouble connecting to my brain right now.",
                        }
        except Exception as e:
            logger.error(f"Failed to connect to Mistral: {e}")
            return {
                "error": str(e),
                "response": "Mistral is not reachable. Is your network ok?",
            }
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

    async def analyze_market(self, market_data: Dict) -> str:
        system_prompt = (
            "You are an expert trading analyst and coach. "
            "Analyze the provided market data and explain price movements in plain language. "
            "Be concise and actionable. If you don't have enough data, say so. "
<<<<<<< HEAD
            "IMPORTANT: Do not hallucinate numbers. Only use the data provided."
=======
            "IMPORTANT: Do not hallucinate numbers. Only use the data provided. "
            "Always include a brief uncertainty note when data is limited."
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51
        )
        
        prompt = f"Current Market Data: {json.dumps(market_data)}\n\nExplain what's happening."
        
        result = await self.generate_response(prompt, system_prompt=system_prompt)
<<<<<<< HEAD
        return result.get("response", "Could not generate analysis.")
=======
        response_text = result.get("response", "Could not generate analysis.")
        return f"{response_text}\n\n{self.compliance_footer}"
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

llm_engine = LLMEngine()
