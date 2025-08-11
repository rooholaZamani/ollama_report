"""
Main application entry point.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Ollama Report Generator",
    description="A service for generating reports using Ollama models",
    version="1.0.0"
)

# Import and include routers
from app.api.endpoints import router as api_router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
