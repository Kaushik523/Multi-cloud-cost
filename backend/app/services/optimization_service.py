"""Insight and optimization queries over normalized multicloud telemetry."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func

from backend.app.db import SessionLocal
from backend.app.models.db_models import CloudAccount, CostRecordDB, PerformanceRecordDB
from backend.app.models.schemas import CloudProviderEnum


def _window_start(days: int) -> datetime:
    """Return UTC timestamp representing the start of the requested window."""

    safe_days = max(int(days or 0), 1)
    return datetime.utcnow() - timedelta(days=safe_days)


def _cost_totals_by_provider(session, window_start: datetime) -> dict[str, float]:
    """Aggregate total cost for each provider within the window."""

    totals = {provider.value: 0.0 for provider in CloudProviderEnum}
    rows = (
        session.query(
            CostRecordDB.provider,
            func.coalesce(func.sum(CostRecordDB.cost_amount), 0.0).label("total_cost"),
        )
        .filter(CostRecordDB.timestamp >= window_start)
        .group_by(CostRecordDB.provider)
        .all()
    )
    for provider, total_cost in rows:
        totals[provider] = float(total_cost or 0.0)
    return totals


def get_overview_summary(time_window_days: int) -> dict[str, Any]:
    """Return high-level cost insights for dashboard overviews."""

    window_start = _window_start(time_window_days)
    session = SessionLocal()
    try:
        total_cost_per_provider = _cost_totals_by_provider(session, window_start)
        top_services_rows = (
            session.query(
                CostRecordDB.provider,
                CostRecordDB.service,
                func.coalesce(func.sum(CostRecordDB.cost_amount), 0.0).label("total_cost"),
            )
            .filter(CostRecordDB.timestamp >= window_start)
            .group_by(CostRecordDB.provider, CostRecordDB.service)
            .order_by(func.sum(CostRecordDB.cost_amount).desc())
            .limit(5)
            .all()
        )
        top_services = [
            {
                "provider": row.provider,
                "service": row.service,
                "total_cost": float(row.total_cost or 0.0),
            }
            for row in top_services_rows
        ]
        return {
            "time_window_days": max(int(time_window_days or 0), 1),
            "total_cost_per_provider": total_cost_per_provider,
            "top_services": top_services,
        }
    finally:
        session.close()


def get_comparison_summary(time_window_days: int) -> list[dict[str, Any]]:
    """Return per-provider metrics suitable for comparative tables."""

    window_start = _window_start(time_window_days)
    session = SessionLocal()
    try:
        comparison = {
            provider.value: {
                "provider": provider.value,
                "total_cost": 0.0,
                "avg_cpu_utilization": None,
                "workload_count": 0,
            }
            for provider in CloudProviderEnum
        }

        cost_rows = (
            session.query(
                CostRecordDB.provider,
                func.coalesce(func.sum(CostRecordDB.cost_amount), 0.0).label("total_cost"),
            )
            .filter(CostRecordDB.timestamp >= window_start)
            .group_by(CostRecordDB.provider)
            .all()
        )
        for provider, total_cost in cost_rows:
            comparison[provider]["total_cost"] = float(total_cost or 0.0)

        perf_rows = (
            session.query(
                PerformanceRecordDB.provider,
                func.avg(PerformanceRecordDB.cpu_utilization).label("avg_cpu"),
                func.count(func.distinct(PerformanceRecordDB.resource_id)).label("workload_count"),
            )
            .filter(PerformanceRecordDB.timestamp >= window_start)
            .group_by(PerformanceRecordDB.provider)
            .all()
        )
        for provider, avg_cpu, workload_count in perf_rows:
            comparison[provider]["avg_cpu_utilization"] = (
                float(avg_cpu) if avg_cpu is not None else None
            )
            comparison[provider]["workload_count"] = int(workload_count or 0)

        return list(comparison.values())
    finally:
        session.close()


def _lookup_accounts(session) -> dict[int, str]:
    """Return mapping from account primary key to human-friendly identifier."""

    rows = session.query(CloudAccount.id, CloudAccount.account_identifier).all()
    return {row.id: row.account_identifier for row in rows}


def _collect_workloads(session, window_start: datetime) -> list[dict[str, Any]]:
    """Aggregate workload cost and performance metrics for comparison."""

    workload_map: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    cost_rows = (
        session.query(
            CostRecordDB.provider,
            CostRecordDB.account_id,
            CostRecordDB.service,
            CostRecordDB.region,
            func.coalesce(func.sum(CostRecordDB.cost_amount), 0.0).label("total_cost"),
        )
        .filter(CostRecordDB.timestamp >= window_start)
        .group_by(
            CostRecordDB.provider,
            CostRecordDB.account_id,
            CostRecordDB.service,
            CostRecordDB.region,
        )
        .all()
    )

    for row in cost_rows:
        key = (row.provider, row.account_id, row.service, row.region)
        workload_map[key] = {
            "provider": row.provider,
            "account_id": row.account_id,
            "service": row.service,
            "region": row.region,
            "total_cost": float(row.total_cost or 0.0),
            "avg_cpu": None,
        }

    perf_rows = (
        session.query(
            PerformanceRecordDB.provider,
            PerformanceRecordDB.account_id,
            PerformanceRecordDB.service,
            PerformanceRecordDB.region,
            func.avg(PerformanceRecordDB.cpu_utilization).label("avg_cpu"),
        )
        .filter(PerformanceRecordDB.timestamp >= window_start)
        .group_by(
            PerformanceRecordDB.provider,
            PerformanceRecordDB.account_id,
            PerformanceRecordDB.service,
            PerformanceRecordDB.region,
        )
        .all()
    )

    for row in perf_rows:
        key = (row.provider, row.account_id, row.service, row.region)
        workload = workload_map.setdefault(
            key,
            {
                "provider": row.provider,
                "account_id": row.account_id,
                "service": row.service,
                "region": row.region,
                "total_cost": 0.0,
                "avg_cpu": None,
            },
        )
        workload["avg_cpu"] = float(row.avg_cpu or 0.0)

    account_lookup = _lookup_accounts(session)
    for workload in workload_map.values():
        account_identifier = account_lookup.get(workload["account_id"], str(workload["account_id"]))
        workload["workload_id"] = f"{account_identifier}:{workload['service']}@{workload['region']}"

    return list(workload_map.values())


def get_optimization_suggestions(
    time_window_days: int, savings_threshold: float = 0.15
) -> list[dict[str, Any]]:
    """Suggest cross-cloud workload placements that reduce cost with similar CPU usage."""

    window_start = _window_start(time_window_days)
    session = SessionLocal()
    try:
        workloads = _collect_workloads(session, window_start)
        if not workloads:
            return []

        groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for workload in workloads:
            service_key = (workload["service"].lower(), workload["region"].lower())
            groups[service_key].append(workload)

        suggestions: list[dict[str, Any]] = []
        for entries in groups.values():
            if len(entries) < 2:
                continue
            for current in entries:
                current_cost = current.get("total_cost") or 0.0
                current_cpu = current.get("avg_cpu")
                if current_cost <= 0.0 or current_cpu is None:
                    continue

                best_alternative: dict[str, Any] | None = None
                best_savings = 0.0
                for candidate in entries:
                    if candidate is current:
                        continue
                    alt_cost = candidate.get("total_cost") or 0.0
                    alt_cpu = candidate.get("avg_cpu")
                    if alt_cost <= 0.0 or alt_cpu is None:
                        continue

                    if abs(alt_cpu - current_cpu) > 10.0:
                        continue
                    savings = (current_cost - alt_cost) / current_cost
                    if savings >= savings_threshold and (best_alternative is None or alt_cost < best_alternative["total_cost"]):
                        best_alternative = candidate
                        best_savings = savings

                if best_alternative is None:
                    continue

                suggestions.append(
                    {
                        "workload_id": current["workload_id"],
                        "current_provider": current["provider"],
                        "recommended_provider": best_alternative["provider"],
                        "estimated_savings_percent": round(best_savings * 100, 2),
                        "explanation": (
                            f"Move {current['service']} in {current['region']} from {current['provider']} "
                            f"(~{round(current_cpu, 1)}% CPU, cost {current_cost:.2f}) to "
                            f"{best_alternative['provider']} (~{round(best_alternative['avg_cpu'] or 0.0, 1)}% CPU, "
                            f"cost {best_alternative['total_cost']:.2f}) to save ~{round(best_savings * 100, 2)}%."
                        ),
                    }
                )

        return suggestions
    finally:
        session.close()


__all__ = [
    "get_overview_summary",
    "get_comparison_summary",
    "get_optimization_suggestions",
]
