"""
Main application entry point.
"""
from fastapi import FastAPI, APIRouter
# Import routers from the new endpoint files
from app.api.endpoints import incidents, vulnerabilities, models, checklist, assessments

app = FastAPI(
    title="Ollama Report Generator",
    description="A service for generating reports using Ollama models",
    version="1.0.0"
)

# A main router to organize all endpoints under a common path like /api
api_router = APIRouter(prefix="/api")

api_router.include_router(models.router)
api_router.include_router(checklist.router)
api_router.include_router(incidents.router)
api_router.include_router(vulnerabilities.router)
api_router.include_router(assessments.router)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)