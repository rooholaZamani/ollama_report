"""
Ollama API client implementation.
"""
import httpx
from typing import Dict, Any
import os

class OllamaClient:
    def __init__(self, base_url: str = "http://192.168.1.50:11434"):
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url)
        self.client = httpx.AsyncClient(timeout=120.0)
    
    
    async def generate(self, model: str, prompt: str) -> str:
        """
        Generate text using the specified Ollama model.
        """
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False  # Set to True if you want streaming responses
            }
        )
        response.raise_for_status() # Ensure we raise an error for bad responses
        return response.json()["response"]
    
    async def list_models(self) -> Dict[str, Any]:
        """
        List available models.
        """
        response = await self.client.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        return response.json()