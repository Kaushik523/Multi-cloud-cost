"""Utilities for normalizing cloud provider telemetry payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from backend.app.models.schemas import (
    CloudProviderEnum,
    CostRecord,
    PerformanceRecord,
)
from backend.app.providers import aws_client, azure_client, gcp_client

RawRecord = dict[str, Any]

_DEFAULT_ACCOUNTS = {
    CloudProviderEnum.AWS: "aws-default-account",
    CloudProviderEnum.AZURE: "subscriptions/default",
    CloudProviderEnum.GCP: "projects/default",
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _safe_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.utcnow()


def _resource_hint(*candidates: Any) -> str:
    for candidate in candidates:
        if candidate is None:
            continue
        candidate_str = str(candidate).strip()
        if candidate_str:
            return candidate_str
    return "resource"


def _metric_to_performance_fields(metric_name: str, value: float) -> tuple[float, float, float]:
    metric_lower = metric_name.lower()
    if "cpu" in metric_lower:
        return value, 0.0, 0.0
    if any(token in metric_lower for token in ("memory", "storage", "dtu", "slot")):
        return 0.0, value, 0.0
    if any(token in metric_lower for token in ("latency", "network", "io", "throughput")):
        return 0.0, 0.0, value
    return value, 0.0, 0.0


def _normalize_aws_cost(provider: CloudProviderEnum, record: RawRecord) -> CostRecord:
    return CostRecord(
        provider=provider,
        account_id=_DEFAULT_ACCOUNTS[provider],
        service=_safe_str(record.get("service"), "AmazonService"),
        region=_safe_str(record.get("region"), "global"),
        usage_amount=_safe_float(record.get("usage_amount")),
        usage_unit=_safe_str(record.get("usage_type"), "Units"),
        cost_amount=_safe_float(record.get("cost")),
        currency=_safe_str(record.get("currency"), "USD"),
        timestamp=_safe_timestamp(record.get("timestamp")),
    )


def _normalize_azure_cost(provider: CloudProviderEnum, record: RawRecord) -> CostRecord:
    return CostRecord(
        provider=provider,
        account_id=_safe_str(record.get("resourceGroup"), _DEFAULT_ACCOUNTS[provider]),
        service=_safe_str(record.get("meterCategory"), "AzureService"),
        region=_safe_str(record.get("meterRegion"), "global"),
        usage_amount=_safe_float(record.get("quantity")),
        usage_unit=_safe_str(record.get("unit"), "Units"),
        cost_amount=_safe_float(record.get("cost")),
        currency=_safe_str(record.get("currency"), "USD"),
        timestamp=_safe_timestamp(record.get("timestamp")),
    )


def _normalize_gcp_cost(provider: CloudProviderEnum, record: RawRecord) -> CostRecord:
    return CostRecord(
        provider=provider,
        account_id=_safe_str(record.get("project"), _DEFAULT_ACCOUNTS[provider]),
        service=_safe_str(record.get("sku"), "GCPService"),
        region=_safe_str(record.get("location"), "global"),
        usage_amount=_safe_float(record.get("usage")),
        usage_unit=_safe_str(record.get("usage_unit"), "Units"),
        cost_amount=_safe_float(record.get("cost")),
        currency=_safe_str(record.get("currency"), "USD"),
        timestamp=_safe_timestamp(record.get("timestamp")),
    )


def _normalize_aws_performance(provider: CloudProviderEnum, record: RawRecord) -> PerformanceRecord:
    cpu, memory, network = _metric_to_performance_fields(
        _safe_str(record.get("metric")), _safe_float(record.get("value"))
    )
    return PerformanceRecord(
        provider=provider,
        account_id=_DEFAULT_ACCOUNTS[provider],
        resource_id=_resource_hint(
            record.get("instance_type"), record.get("bucket_class"), record.get("engine"), record.get("service")
        ),
        service=_safe_str(record.get("service"), "AmazonService"),
        region=_safe_str(record.get("region"), "global"),
        cpu_utilization=cpu,
        memory_utilization=memory,
        network_io=network,
        timestamp=_safe_timestamp(record.get("timestamp")),
    )


def _normalize_azure_performance(provider: CloudProviderEnum, record: RawRecord) -> PerformanceRecord:
    cpu, memory, network = _metric_to_performance_fields(
        _safe_str(record.get("metricName")), _safe_float(record.get("average"))
    )
    return PerformanceRecord(
        provider=provider,
        account_id=_DEFAULT_ACCOUNTS[provider],
        resource_id=_resource_hint(record.get("vmSize"), record.get("accountType"), record.get("tier")),
        service=_safe_str(record.get("resourceType"), "AzureResource"),
        region=_safe_str(record.get("meterRegion"), "global"),
        cpu_utilization=cpu,
        memory_utilization=memory,
        network_io=network,
        timestamp=_safe_timestamp(record.get("timestamp")),
    )


def _normalize_gcp_performance(provider: CloudProviderEnum, record: RawRecord) -> PerformanceRecord:
    cpu, memory, network = _metric_to_performance_fields(
        _safe_str(record.get("metric")), _safe_float(record.get("value"))
    )
    return PerformanceRecord(
        provider=provider,
        account_id=_DEFAULT_ACCOUNTS[provider],
        resource_id=_resource_hint(record.get("machine_type"), record.get("storage_class"), record.get("reservation")),
        service=_safe_str(record.get("service"), "GCPService"),
        region=_safe_str(record.get("location"), "global"),
        cpu_utilization=cpu,
        memory_utilization=memory,
        network_io=network,
        timestamp=_safe_timestamp(record.get("timestamp")),
    )


_COST_NORMALIZERS: dict[CloudProviderEnum, Callable[[CloudProviderEnum, RawRecord], CostRecord]] = {
    CloudProviderEnum.AWS: _normalize_aws_cost,
    CloudProviderEnum.AZURE: _normalize_azure_cost,
    CloudProviderEnum.GCP: _normalize_gcp_cost,
}


_PERFORMANCE_NORMALIZERS: dict[CloudProviderEnum, Callable[[CloudProviderEnum, RawRecord], PerformanceRecord]] = {
    CloudProviderEnum.AWS: _normalize_aws_performance,
    CloudProviderEnum.AZURE: _normalize_azure_performance,
    CloudProviderEnum.GCP: _normalize_gcp_performance,
}


__all__ = [
    "normalize_cost_records",
    "normalize_performance_records",
    "fetch_and_normalize_all_providers",
]


def normalize_cost_records(provider: CloudProviderEnum, raw_records: list[RawRecord]) -> list[CostRecord]:
    """Convert provider-specific cost payloads into unified CostRecord objects."""

    normalizer = _COST_NORMALIZERS.get(provider)
    if normalizer is None:
        raise ValueError(f"Unsupported provider: {provider}")

    return [normalizer(provider, record) for record in raw_records or []]


def normalize_performance_records(
    provider: CloudProviderEnum, raw_records: list[RawRecord]
) -> list[PerformanceRecord]:
    """Convert provider-specific telemetry payloads into PerformanceRecord objects."""

    normalizer = _PERFORMANCE_NORMALIZERS.get(provider)
    if normalizer is None:
        raise ValueError(f"Unsupported provider: {provider}")

    return [normalizer(provider, record) for record in raw_records or []]


def fetch_and_normalize_all_providers(
    start_date: datetime, end_date: datetime
) -> tuple[list[CostRecord], list[PerformanceRecord]]:
    """Fetch mock data from every provider and return normalized results."""

    provider_modules = (
        (CloudProviderEnum.AWS, aws_client),
        (CloudProviderEnum.AZURE, azure_client),
        (CloudProviderEnum.GCP, gcp_client),
    )

    all_costs: list[CostRecord] = []
    all_performance: list[PerformanceRecord] = []

    for provider, module in provider_modules:
        raw_cost = module.get_mock_cost_data(start_date, end_date)
        raw_performance = module.get_mock_performance_data(start_date, end_date)
        all_costs.extend(normalize_cost_records(provider, raw_cost))
        all_performance.extend(normalize_performance_records(provider, raw_performance))

    return all_costs, all_performance
