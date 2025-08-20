"""
Report generation service.
"""
from app.services.ollama_client import OllamaClient
from app.models.report import Report

class ReportGenerator:
    def __init__(self):
        self.ollama_client = OllamaClient()
    
    async def generate_report(self, model: str, prompt: str) -> Report:
        """
        Generate a report using the specified model and prompt.
        """
        content = await self.ollama_client.generate(model, prompt)
        
        return Report(
            title=f"Report generated with {model}",
            content=content,
            model_used=model
        )
