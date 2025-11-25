from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List


def _spread_timestamps(start_date: datetime, end_date: datetime, count: int) -> List[datetime]:
    """Return evenly spaced timestamps clamped to the last 30 days."""
    if count <= 0:
        return []

    now = datetime.utcnow()
    latest = min(end_date, now)
    earliest = max(start_date, latest - timedelta(days=30))

    if latest <= earliest:
        earliest = latest - timedelta(days=1)

    span = latest - earliest
    return [earliest + span * ((idx + 1) / (count + 1)) for idx in range(count)]


def get_mock_cost_data(start_date: datetime, end_date: datetime) -> List[Dict]:
    timestamps = _spread_timestamps(start_date, end_date, 3)
    base_data = [
        {
            "service": "Amazon EC2",
            "region": "us-east-1",
            "usage_amount": 120.5,
            "usage_type": "BoxUsage:m5.large",
            "cost": 245.75,
            "currency": "USD",
        },
        {
            "service": "Amazon S3",
            "region": "us-west-2",
            "usage_amount": 3.2,
            "usage_type": "TimedStorage-ByteHrs",
            "cost": 58.40,
            "currency": "USD",
        },
        {
            "service": "Amazon RDS",
            "region": "eu-central-1",
            "usage_amount": 90.0,
            "usage_type": "InstanceUsage:db.m5.large",
            "cost": 310.10,
            "currency": "USD",
        },
    ]

    return [
        {**record, "timestamp": timestamps[idx]}
        for idx, record in enumerate(base_data)
    ]


def get_mock_performance_data(start_date: datetime, end_date: datetime) -> List[Dict]:
    timestamps = _spread_timestamps(start_date, end_date, 3)
    performance_data = [
        {
            "service": "Amazon EC2",
            "region": "us-east-1",
            "metric_name": "cpu_utilization",
            "metric_unit": "percent",
            "value": 67.8,
        },
        {
            "service": "Amazon S3",
            "region": "us-west-2",
            "metric_name": "request_latency_p95",
            "metric_unit": "ms",
            "value": 23.4,
        },
        {
            "service": "Amazon RDS",
            "region": "eu-central-1",
            "metric_name": "db_connections",
            "metric_unit": "count",
            "value": 125,
        },
    ]

    return [
        {**record, "timestamp": timestamps[idx]}
        for idx, record in enumerate(performance_data)
    ]
