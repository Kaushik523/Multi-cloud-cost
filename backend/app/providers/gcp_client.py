"""Mock GCP cost and performance client."""

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
    """Return representative GCP cost data for Compute, Storage, and BigQuery."""
    normalized_start, normalized_end = _normalize_range(start_date, end_date)
    reference_end = normalized_end
    timestamps = [
        reference_end - timedelta(days=6),
        reference_end - timedelta(days=14),
        reference_end - timedelta(days=25),
    ]

    return [
        {
            "sku": "Compute Engine N2",
            "location": "us-central1",
            "usage": 110,
            "usage_unit": "Hours",
            "cost": 198.75,
            "currency": "USD",
            "project": "prod-core",
            "timestamp": _clamp_timestamp(timestamps[0], normalized_start, normalized_end),
        },
        {
            "sku": "Cloud Storage Standard",
            "location": "asia-southeast1",
            "usage": 7_400,
            "usage_unit": "GB-Month",
            "cost": 32.1,
            "currency": "USD",
            "project": "analytics-etl",
            "timestamp": _clamp_timestamp(timestamps[1], normalized_start, normalized_end),
        },
        {
            "sku": "BigQuery Slots",
            "location": "europe-west4",
            "usage": 56,
            "usage_unit": "SlotHours",
            "cost": 142.3,
            "currency": "USD",
            "project": "finance-warehouse",
            "timestamp": _clamp_timestamp(timestamps[2], normalized_start, normalized_end),
        },
    ]


def get_mock_performance_data(start_date: datetime, end_date: datetime) -> List[dict]:
    """Return representative GCP performance data."""
    normalized_start, normalized_end = _normalize_range(start_date, end_date)
    reference_end = normalized_end
    timestamps = [
        reference_end - timedelta(days=1),
        reference_end - timedelta(days=7),
        reference_end - timedelta(days=19),
    ]

    return [
        {
            "service": "Compute Engine",
            "location": "us-central1",
            "metric": "CPU utilization",
            "value": 64.1,
            "unit": "Percent",
            "machine_type": "n2-standard-4",
            "timestamp": _clamp_timestamp(timestamps[0], normalized_start, normalized_end),
        },
        {
            "service": "Cloud Storage",
            "location": "asia-southeast1",
            "metric": "Request latency",
            "value": 28,
            "unit": "Milliseconds",
            "storage_class": "STANDARD",
            "timestamp": _clamp_timestamp(timestamps[1], normalized_start, normalized_end),
        },
        {
            "service": "BigQuery",
            "location": "europe-west4",
            "metric": "Slot utilization",
            "value": 71.4,
            "unit": "Percent",
            "reservation": "prod-bi-slots",
            "timestamp": _clamp_timestamp(timestamps[2], normalized_start, normalized_end),
        },
    ]
