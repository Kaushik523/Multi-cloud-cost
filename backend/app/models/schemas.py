from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CloudProviderEnum(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"


class HealthResponse(BaseModel):
    """Schema used by the health check endpoint."""

    status: str = Field(..., description="Overall service status indicator.")

    class Config:
        json_schema_extra = {"example": {"status": "ok"}}


class CostRecord(BaseModel):
    provider: CloudProviderEnum = Field(..., description="Cloud vendor that generated the cost.")
    account_id: str = Field(..., description="Billing account identifier.")
    service: str = Field(..., description="Cloud service name, e.g., EC2.")
    region: str = Field(..., description="Region where the cost originated.")
    usage_amount: float = Field(..., description="Amount of usage consumed.")
    usage_unit: str = Field(..., description="Unit for the usage amount, e.g., hours.")
    cost_amount: float = Field(..., description="Amount billed for the usage.")
    currency: str = Field(..., description="Currency of the cost, e.g., USD.")
    timestamp: datetime = Field(..., description="When the cost was recorded.")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "AWS",
                "account_id": "123456789012",
                "service": "EC2",
                "region": "us-east-1",
                "usage_amount": 120.5,
                "usage_unit": "hours",
                "cost_amount": 345.67,
                "currency": "USD",
                "timestamp": "2024-01-15T10:00:00Z",
            }
        }


class PerformanceRecord(BaseModel):
    provider: CloudProviderEnum = Field(..., description="Cloud vendor emitting performance metrics.")
    account_id: str = Field(..., description="Billing account identifier.")
    resource_id: str = Field(..., description="Unique identifier for the monitored resource.")
    service: str = Field(..., description="Service offering the resource, e.g., Compute Engine.")
    region: str = Field(..., description="Region where the resource runs.")
    cpu_utilization: float = Field(..., description="Average CPU utilization percentage.")
    memory_utilization: float = Field(..., description="Average memory utilization percentage.")
    network_io: float = Field(..., description="Network throughput in Mbps.")
    timestamp: datetime = Field(..., description="When the performance measurement was captured.")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "GCP",
                "account_id": "projects/example-project",
                "resource_id": "instances/instance-1",
                "service": "Compute Engine",
                "region": "us-central1",
                "cpu_utilization": 72.3,
                "memory_utilization": 65.1,
                "network_io": 150.4,
                "timestamp": "2024-01-15T10:05:00Z",
            }
        }


__all__ = ["CloudProviderEnum", "HealthResponse", "CostRecord", "PerformanceRecord"]
