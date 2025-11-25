from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List


def _spread_timestamps(start_date: datetime, end_date: datetime, count: int) -> List[datetime]:
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
            "sku": "Compute Engine N2 Standard",
            "location": "us-central1",
            "usage": 110.0,
            "usage_unit": "Hour",
            "cost": 198.25,
            "currency": "USD",
        },
        {
            "sku": "Cloud Storage Standard",
            "location": "asia-southeast1",
            "usage": 4.6,
            "usage_unit": "TB-Month",
            "cost": 42.75,
            "currency": "USD",
        },
        {
            "sku": "Cloud SQL Postgres",
            "location": "europe-west1",
            "usage": 80.0,
            "usage_unit": "Instance Hour",
            "cost": 256.90,
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
            "service": "Compute Engine",
            "location": "us-central1",
            "metric": "cpu_load",
            "unit": "percent",
            "value": 64.1,
        },
        {
            "service": "Cloud Storage",
            "location": "asia-southeast1",
            "metric": "egress_bandwidth",
            "unit": "MBps",
            "value": 145.6,
        },
        {
            "service": "Cloud SQL",
            "location": "europe-west1",
            "metric": "active_connections",
            "unit": "count",
            "value": 98,
        },
    ]

    return [
        {**record, "timestamp": timestamps[idx]}
        for idx, record in enumerate(performance_data)
    ]
