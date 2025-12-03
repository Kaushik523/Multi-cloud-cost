"""Mock AWS cost and performance client."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List


def _normalize_range(start_date: datetime, end_date: datetime) -> tuple[datetime, datetime]:
    """Clamp the requested range to the last 30 days ending no later than now."""
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
    """Return representative AWS cost entries for EC2, S3, and RDS."""
    normalized_start, normalized_end = _normalize_range(start_date, end_date)
    reference_end = normalized_end
    timestamps = [
        reference_end - timedelta(days=5),
        reference_end - timedelta(days=12),
        reference_end - timedelta(days=20),
    ]

    return [
        {
            "service": "AmazonEC2",
            "region": "us-east-1",
            "usage_amount": 140.2,
            "usage_type": "BoxUsage:m5.large",
            "cost": 210.35,
            "currency": "USD",
            "timestamp": _clamp_timestamp(timestamps[0], normalized_start, normalized_end),
        },
        {
            "service": "AmazonS3",
            "region": "us-west-2",
            "usage_amount": 18_500,
            "usage_type": "TimedStorage-ByteHrs",
            "cost": 44.12,
            "currency": "USD",
            "timestamp": _clamp_timestamp(timestamps[1], normalized_start, normalized_end),
        },
        {
            "service": "AmazonRDS",
            "region": "eu-central-1",
            "usage_amount": 320,
            "usage_type": "InstanceUsage:db.r6g.large",
            "cost": 168.9,
            "currency": "USD",
            "timestamp": _clamp_timestamp(timestamps[2], normalized_start, normalized_end),
        },
    ]


def get_mock_performance_data(start_date: datetime, end_date: datetime) -> List[dict]:
    """Return representative AWS performance metrics."""
    normalized_start, normalized_end = _normalize_range(start_date, end_date)
    reference_end = normalized_end
    timestamps = [
        reference_end - timedelta(days=3),
        reference_end - timedelta(days=9),
        reference_end - timedelta(days=16),
    ]

    return [
        {
            "service": "AmazonEC2",
            "region": "us-east-1",
            "metric": "CPUUtilization",
            "value": 67.3,
            "unit": "Percent",
            "instance_type": "m5.large",
            "timestamp": _clamp_timestamp(timestamps[0], normalized_start, normalized_end),
        },
        {
            "service": "AmazonS3",
            "region": "us-west-2",
            "metric": "FirstByteLatency",
            "value": 35,
            "unit": "Milliseconds",
            "bucket_class": "STANDARD",
            "timestamp": _clamp_timestamp(timestamps[1], normalized_start, normalized_end),
        },
        {
            "service": "AmazonRDS",
            "region": "eu-central-1",
            "metric": "FreeStorageSpace",
            "value": 85,
            "unit": "Percent",
            "engine": "aurora-postgresql",
            "timestamp": _clamp_timestamp(timestamps[2], normalized_start, normalized_end),
        },
    ]
