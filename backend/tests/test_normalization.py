"""Tests for provider normalization service."""
from datetime import datetime, timedelta

import pytest

from backend.app.models.schemas import CloudProviderEnum, CostRecord, PerformanceRecord
from backend.app.providers import aws_client, azure_client, gcp_client
from backend.app.services.normalization_service import (
    normalize_cost_records,
    normalize_performance_records,
)


@pytest.fixture
def date_range() -> tuple[datetime, datetime]:
    end = datetime.utcnow()
    start = end - timedelta(days=29)
    return start, end


@pytest.mark.parametrize(
    ("provider", "module", "expected"),
    [
        (
            CloudProviderEnum.AWS,
            aws_client,
            {
                "account_id": "aws-default-account",
                "service": "AmazonEC2",
                "region": "us-east-1",
                "usage_amount": 140.2,
                "usage_unit": "BoxUsage:m5.large",
                "cost_amount": 210.35,
                "currency": "USD",
            },
        ),
        (
            CloudProviderEnum.AZURE,
            azure_client,
            {
                "account_id": "rg-prod-core",
                "service": "Virtual Machines",
                "region": "eastus",
                "usage_amount": 96,
                "usage_unit": "Hours",
                "cost_amount": 184.6,
                "currency": "USD",
            },
        ),
        (
            CloudProviderEnum.GCP,
            gcp_client,
            {
                "account_id": "prod-core",
                "service": "Compute Engine N2",
                "region": "us-central1",
                "usage_amount": 110,
                "usage_unit": "Hours",
                "cost_amount": 198.75,
                "currency": "USD",
            },
        ),
    ],
)
def test_normalize_cost_records_maps_known_fields(provider, module, expected, date_range):
    start, end = date_range
    raw_records = module.get_mock_cost_data(start, end)
    normalized = normalize_cost_records(provider, raw_records)

    assert normalized, "expected cost records to be normalized"
    first = normalized[0]
    assert isinstance(first, CostRecord)

    for field, value in expected.items():
        actual = getattr(first, field)
        if isinstance(value, float):
            assert actual == pytest.approx(value)
        else:
            assert actual == value

    assert isinstance(first.timestamp, datetime)


@pytest.mark.parametrize(
    ("provider", "module", "expected"),
    [
        (
            CloudProviderEnum.AWS,
            aws_client,
            {
                "account_id": "aws-default-account",
                "resource_id": "m5.large",
                "service": "AmazonEC2",
                "region": "us-east-1",
                "cpu_utilization": 67.3,
                "memory_utilization": 0.0,
                "network_io": 0.0,
            },
        ),
        (
            CloudProviderEnum.AZURE,
            azure_client,
            {
                "account_id": "subscriptions/default",
                "resource_id": "Standard_D4s_v5",
                "service": "VirtualMachine",
                "region": "eastus",
                "cpu_utilization": 61.5,
                "memory_utilization": 0.0,
                "network_io": 0.0,
            },
        ),
        (
            CloudProviderEnum.GCP,
            gcp_client,
            {
                "account_id": "projects/default",
                "resource_id": "n2-standard-4",
                "service": "Compute Engine",
                "region": "us-central1",
                "cpu_utilization": 64.1,
                "memory_utilization": 0.0,
                "network_io": 0.0,
            },
        ),
    ],
)
def test_normalize_performance_records_correctly_maps_metrics(provider, module, expected, date_range):
    start, end = date_range
    raw_records = module.get_mock_performance_data(start, end)
    normalized = normalize_performance_records(provider, raw_records)

    assert normalized, "expected performance records to be normalized"
    first = normalized[0]
    assert isinstance(first, PerformanceRecord)

    for field, value in expected.items():
        actual = getattr(first, field)
        if isinstance(value, float):
            assert actual == pytest.approx(value)
        else:
            assert actual == value

    assert isinstance(first.timestamp, datetime)
