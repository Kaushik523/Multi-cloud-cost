from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema used by the health check endpoint."""

    status: str = Field(..., description="Overall service status indicator.")

    class Config:
        json_schema_extra = {"example": {"status": "ok"}}


__all__ = ["HealthResponse"]
