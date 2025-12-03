"""Unified Pydantic schemas used across API layers."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class CloudProviderEnum(str, Enum):
    """Supported cloud providers."""

    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"


class CostRecord(BaseModel):
    """Normalized cost reporting payload."""

    provider: CloudProviderEnum
    account_id: str
    service: str
    region: str
    usage_amount: float
    usage_unit: str
    cost_amount: float
    currency: str
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "AWS",
                "account_id": "123456789012",
                "service": "AmazonEC2",
                "region": "us-east-1",
                "usage_amount": 120.5,
                "usage_unit": "Hours",
                "cost_amount": 345.67,
                "currency": "USD",
                "timestamp": "2024-07-15T12:34:56Z",
            }
        }
    )


class PerformanceRecord(BaseModel):
    """Normalized performance telemetry payload."""

    provider: CloudProviderEnum
    account_id: str
    resource_id: str
    service: str
    region: str
    cpu_utilization: float
    memory_utilization: float
    network_io: float
    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "GCP",
                "account_id": "projects/sample-project",
                "resource_id": "instances/instance-1",
                "service": "ComputeEngine",
                "region": "us-central1",
                "cpu_utilization": 67.3,
                "memory_utilization": 58.1,
                "network_io": 125.4,
                "timestamp": "2024-07-15T12:34:56Z",
            }
        }
    )


class OverviewTopService(BaseModel):
    """Service entry in the overview summary."""

    provider: CloudProviderEnum
    service: str
    total_cost: float


class OverviewSummaryResponse(BaseModel):
    """High-level dashboard summary."""

    time_window_days: int
    total_cost_per_provider: dict[CloudProviderEnum, float]
    top_services: list[OverviewTopService]


class ComparisonSummaryResponse(BaseModel):
    """Provider-level metrics for comparisons."""

    provider: CloudProviderEnum
    total_cost: float
    avg_cpu_utilization: float | None
    workload_count: int


class RecommendationResponse(BaseModel):
    """Optimization recommendation for a workload."""

    workload_id: str
    current_provider: CloudProviderEnum
    recommended_provider: CloudProviderEnum
    estimated_savings_percent: float
    explanation: str
