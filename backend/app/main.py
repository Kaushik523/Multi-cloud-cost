from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    ComparisonSummaryResponse,
    OverviewSummaryResponse,
    RecommendationResponse,
)
from app.services.optimization_service import (
    get_comparison_summary,
    get_optimization_suggestions,
    get_overview_summary,
)

app = FastAPI(title="Multicloud API", version="0.1.0")

# Allow the local frontend to talk to the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Expose a simple health check endpoint."""
    return {"status": "ok"}


@app.get("/summary/overview", response_model=OverviewSummaryResponse)
async def summary_overview(days: int = 30) -> OverviewSummaryResponse:
    """Return high-level spend insights for dashboards."""

    return get_overview_summary(days)


@app.get("/summary/comparison", response_model=list[ComparisonSummaryResponse])
async def summary_comparison(days: int = 30) -> list[ComparisonSummaryResponse]:
    """Return per-provider metrics for comparison tables."""

    return get_comparison_summary(days)


@app.get("/recommendations", response_model=list[RecommendationResponse])
async def recommendations(days: int = 30) -> list[RecommendationResponse]:
    """Return optimization suggestions for cross-cloud workloads."""

    return get_optimization_suggestions(days)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
