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
            "meterCategory": "Virtual Machines",
            "meterRegion": "eastus",
            "serviceName": "Azure VM",
            "quantity": 95.0,
            "unit": "Hours",
            "cost": 210.35,
            "currency": "USD",
        },
        {
            "meterCategory": "Storage",
            "meterRegion": "westeurope",
            "serviceName": "Azure Blob Storage",
            "quantity": 7.5,
            "unit": "TB-Month",
            "cost": 49.80,
            "currency": "USD",
        },
        {
            "meterCategory": "Databases",
            "meterRegion": "centralus",
            "serviceName": "Azure SQL Database",
            "quantity": 120.0,
            "unit": "DTU-Hour",
            "cost": 275.60,
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
            "serviceName": "Azure VM",
            "meterRegion": "eastus",
            "metric": "cpuPercentage",
            "unit": "percent",
            "value": 61.2,
        },
        {
            "serviceName": "Azure Blob Storage",
            "meterRegion": "westeurope",
            "metric": "ingressThroughput",
            "unit": "MBps",
            "value": 180.4,
        },
        {
            "serviceName": "Azure SQL Database",
            "meterRegion": "centralus",
            "metric": "dtuConsumption",
            "unit": "DTU",
            "value": 72.0,
        },
    ]

    return [
        {**record, "timestamp": timestamps[idx]}
        for idx, record in enumerate(performance_data)
    ]
