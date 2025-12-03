"""Mock Azure cost and performance client."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List


def _normalize_range(start_date: datetime, end_date: datetime) -> tuple[datetime, datetime]:
    if start_date > end_date:
        raise ValueError("start_date must be before end_date")

    now = datetime.utcnow()
    normalized_end = min(end_date, now)
    normalized_start = max(start_date, normalized_end - timedelta(days=30))
    return normalized_start, normalized_end


def _clamp_timestamp(ts: datetime, start: datetime, end: datetime) -> datetime:
    if ts < start:
        return start
    if ts > end:
        return end
    return ts


def get_mock_cost_data(start_date: datetime, end_date: datetime) -> List[dict]:
    """Return representative Azure cost data for compute, storage, and SQL."""
    normalized_start, normalized_end = _normalize_range(start_date, end_date)
    reference_end = normalized_end
    timestamps = [
        reference_end - timedelta(days=4),
        reference_end - timedelta(days=11),
        reference_end - timedelta(days=23),
    ]

    return [
        {
            "meterCategory": "Virtual Machines",
            "meterRegion": "eastus",
            "resourceGroup": "rg-prod-core",
            "quantity": 96,
            "unit": "Hours",
            "cost": 184.6,
            "currency": "USD",
            "timestamp": _clamp_timestamp(timestamps[0], normalized_start, normalized_end),
        },
        {
            "meterCategory": "Storage",
            "meterRegion": "westeurope",
            "resourceGroup": "rg-analytics",
            "quantity": 9_200,
            "unit": "GB-Month",
            "cost": 37.8,
            "currency": "USD",
            "timestamp": _clamp_timestamp(timestamps[1], normalized_start, normalized_end),
        },
        {
            "meterCategory": "Azure SQL Database",
            "meterRegion": "centralus",
            "resourceGroup": "rg-finance",
            "quantity": 210,
            "unit": "DTU Hours",
            "cost": 152.4,
            "currency": "USD",
            "timestamp": _clamp_timestamp(timestamps[2], normalized_start, normalized_end),
        },
    ]


def get_mock_performance_data(start_date: datetime, end_date: datetime) -> List[dict]:
    """Return representative Azure performance data."""
    normalized_start, normalized_end = _normalize_range(start_date, end_date)
    reference_end = normalized_end
    timestamps = [
        reference_end - timedelta(days=2),
        reference_end - timedelta(days=8),
        reference_end - timedelta(days=15),
    ]

    return [
        {
            "resourceType": "VirtualMachine",
            "meterRegion": "eastus",
            "metricName": "Percentage CPU",
            "average": 61.5,
            "unit": "Percent",
            "vmSize": "Standard_D4s_v5",
            "timestamp": _clamp_timestamp(timestamps[0], normalized_start, normalized_end),
        },
        {
            "resourceType": "StorageAccount",
            "meterRegion": "westeurope",
            "metricName": "E2E Latency",
            "average": 23,
            "unit": "Milliseconds",
            "accountType": "Standard_LRS",
            "timestamp": _clamp_timestamp(timestamps[1], normalized_start, normalized_end),
        },
        {
            "resourceType": "AzureSQL",
            "meterRegion": "centralus",
            "metricName": "DTU Percentage",
            "average": 72.9,
            "unit": "Percent",
            "tier": "BusinessCritical",
            "timestamp": _clamp_timestamp(timestamps[2], normalized_start, normalized_end),
        },
    ]
