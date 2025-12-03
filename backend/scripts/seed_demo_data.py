"""Seed the local SQLite database with normalized demo data."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence

# Ensure both the repository root (for `backend.*`) and the backend package
# itself (for legacy `app.*` imports) are available on sys.path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
for candidate in (PROJECT_ROOT, BACKEND_DIR):
    path_str = str(candidate)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from backend.app.services.normalization_service import fetch_and_normalize_all_providers
from backend.app.models.schemas import CostRecord, PerformanceRecord
from backend.app.db import SessionLocal
from backend.app.models.db_models import (
    CloudAccount,
    CostRecordDB,
    PerformanceRecordDB,
    create_all_tables,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Populate the database with normalized multicloud demo data."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to seed ending at now (ignored if explicit dates provided).",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="ISO8601 start datetime (e.g., 2024-10-01T00:00:00Z).",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="ISO8601 end datetime (defaults to now when omitted).",
    )
    return parser.parse_args()


def _parse_iso8601(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def resolve_window(args: argparse.Namespace) -> tuple[datetime, datetime]:
    if args.start_date:
        start = _parse_iso8601(args.start_date)
        end = _parse_iso8601(args.end_date) if args.end_date else datetime.utcnow()
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=args.days)

    if start > end:
        raise ValueError("start_date must be before end_date")
    return start, end


def _provider_str(provider: str | CostRecord | PerformanceRecord) -> str:
    if hasattr(provider, "provider"):
        provider_value = getattr(provider, "provider")
    else:
        provider_value = provider
    return getattr(provider_value, "value", provider_value)


def ensure_cloud_accounts(
    session,
    records: Sequence[CostRecord | PerformanceRecord],
) -> dict[tuple[str, str], CloudAccount]:
    """Ensure CloudAccount rows exist for every (provider, account_id)."""

    required_pairs = {
        (_provider_str(record.provider), record.account_id) for record in records
    }

    account_cache: dict[tuple[str, str], CloudAccount] = {}
    for provider, account_identifier in required_pairs:
        account = (
            session.query(CloudAccount)
            .filter(
                CloudAccount.provider == provider,
                CloudAccount.account_identifier == account_identifier,
            )
            .one_or_none()
        )
        if account is None:
            account = CloudAccount(
                provider=provider,
                account_name=account_identifier,
                account_identifier=account_identifier,
            )
            session.add(account)
            session.flush()  # obtain generated primary key
            logging.debug("Created CloudAccount %s/%s", provider, account_identifier)

        account_cache[(provider, account_identifier)] = account

    return account_cache


def purge_existing_records(session, start: datetime, end: datetime) -> tuple[int, int]:
    """Remove cost/performance records in the target window to stay idempotent."""

    cost_deleted = (
        session.query(CostRecordDB)
        .filter(CostRecordDB.timestamp >= start, CostRecordDB.timestamp <= end)
        .delete(synchronize_session=False)
    )
    perf_deleted = (
        session.query(PerformanceRecordDB)
        .filter(PerformanceRecordDB.timestamp >= start, PerformanceRecordDB.timestamp <= end)
        .delete(synchronize_session=False)
    )
    return cost_deleted, perf_deleted


def convert_cost_records(
    cost_records: Sequence[CostRecord],
    account_cache: dict[tuple[str, str], CloudAccount],
) -> list[CostRecordDB]:
    objects: list[CostRecordDB] = []
    for record in cost_records:
        provider = _provider_str(record.provider)
        account = account_cache[(provider, record.account_id)]
        objects.append(
            CostRecordDB(
                provider=provider,
                account_id=account.id,
                service=record.service,
                region=record.region,
                usage_amount=record.usage_amount,
                usage_unit=record.usage_unit,
                cost_amount=record.cost_amount,
                currency=record.currency,
                timestamp=record.timestamp,
            )
        )
    return objects


def convert_performance_records(
    performance_records: Sequence[PerformanceRecord],
    account_cache: dict[tuple[str, str], CloudAccount],
) -> list[PerformanceRecordDB]:
    objects: list[PerformanceRecordDB] = []
    for record in performance_records:
        provider = _provider_str(record.provider)
        account = account_cache[(provider, record.account_id)]
        objects.append(
            PerformanceRecordDB(
                provider=provider,
                account_id=account.id,
                resource_id=record.resource_id,
                service=record.service,
                region=record.region,
                cpu_utilization=record.cpu_utilization,
                memory_utilization=record.memory_utilization,
                network_io=record.network_io,
                timestamp=record.timestamp,
            )
        )
    return objects


def seed_demo_data(start: datetime, end: datetime) -> None:
    create_all_tables()
    session = SessionLocal()

    logging.info("Fetching normalized records for window %s -> %s", start, end)
    cost_records, performance_records = fetch_and_normalize_all_providers(start, end)

    if not cost_records and not performance_records:
        logging.warning("No records returned for the requested window.")
        return

    try:
        cost_deleted, perf_deleted = purge_existing_records(session, start, end)
        logging.info(
            "Purged %s cost records and %s performance records in window.",
            cost_deleted,
            perf_deleted,
        )

        combined_records: list[CostRecord | PerformanceRecord] = [
            *cost_records,
            *performance_records,
        ]
        account_cache = ensure_cloud_accounts(session, combined_records)

        cost_objects = convert_cost_records(cost_records, account_cache)
        perf_objects = convert_performance_records(performance_records, account_cache)

        session.add_all(cost_objects + perf_objects)
        session.commit()
        logging.info(
            "Inserted %s cost records and %s performance records.",
            len(cost_objects),
            len(perf_objects),
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    start, end = resolve_window(args)
    seed_demo_data(start, end)


if __name__ == "__main__":
    main()
