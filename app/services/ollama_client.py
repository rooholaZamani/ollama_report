"""
Ollama API client implementation.
"""
import httpx
from typing import Dict, Any

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def generate(self, model: str, prompt: str) -> str:
        """
        Generate text using the specified Ollama model.
        """
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt
            }
        )
        return response.json()["response"]
    
    async def list_models(self) -> Dict[str, Any]:
        """
        List available models.
        """
        response = await self.client.get(f"{self.base_url}/api/tags")
        return response.json()
