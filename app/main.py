"""
Main application entry point.
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
# Import routers from the new endpoint files
from app.api.endpoints import checklist, incidents, vulnerabilities, models, assessments, executive, processes

app = FastAPI(
    title="Ollama Report Generator",
    description="A service for generating reports using Ollama models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A main router to organize all endpoints under a common path like /api
api_router = APIRouter(prefix="/api")

api_router.include_router(models.router)
api_router.include_router(checklist.router)
api_router.include_router(incidents.router)
api_router.include_router(vulnerabilities.router)
api_router.include_router(assessments.router)
api_router.include_router(executive.router)
api_router.include_router(processes.router)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)