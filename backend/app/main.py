from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .models.schemas import HealthResponse

# Ensure tables exist before the application starts serving requests.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multicloud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Simple health check endpoint for uptime monitoring."""
    return HealthResponse(status="ok")
