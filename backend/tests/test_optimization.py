"""Tests for optimization service recommendations."""
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db import Base
from backend.app.models.db_models import CloudAccount, CostRecordDB, PerformanceRecordDB
from backend.app.models.schemas import CloudProviderEnum
from backend.app.services import optimization_service


def test_get_optimization_suggestions_returns_cheaper_provider(tmp_path, monkeypatch):
    db_path = tmp_path / "optimizations.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(optimization_service, "SessionLocal", testing_session_local)

    session = testing_session_local()
    try:
        aws_account = CloudAccount(
            provider=CloudProviderEnum.AWS.value,
            account_name="aws-prod",
            account_identifier="aws-account",
            tags=None,
        )
        gcp_account = CloudAccount(
            provider=CloudProviderEnum.GCP.value,
            account_name="gcp-prod",
            account_identifier="gcp-account",
            tags=None,
        )
        session.add_all([aws_account, gcp_account])
        session.commit()

        now = datetime.utcnow()

        session.add_all(
            [
                CostRecordDB(
                    provider=CloudProviderEnum.AWS.value,
                    account_id=aws_account.id,
                    service="Compute",
                    region="us-east-1",
                    usage_amount=100,
                    usage_unit="Hours",
                    cost_amount=200.0,
                    currency="USD",
                    timestamp=now,
                ),
                CostRecordDB(
                    provider=CloudProviderEnum.GCP.value,
                    account_id=gcp_account.id,
                    service="Compute",
                    region="us-east-1",
                    usage_amount=100,
                    usage_unit="Hours",
                    cost_amount=120.0,
                    currency="USD",
                    timestamp=now,
                ),
                PerformanceRecordDB(
                    provider=CloudProviderEnum.AWS.value,
                    account_id=aws_account.id,
                    resource_id="aws-workload",
                    service="Compute",
                    region="us-east-1",
                    cpu_utilization=65.0,
                    memory_utilization=55.0,
                    network_io=12.0,
                    timestamp=now,
                ),
                PerformanceRecordDB(
                    provider=CloudProviderEnum.GCP.value,
                    account_id=gcp_account.id,
                    resource_id="gcp-workload",
                    service="Compute",
                    region="us-east-1",
                    cpu_utilization=63.5,
                    memory_utilization=54.0,
                    network_io=11.0,
                    timestamp=now,
                ),
            ]
        )
        session.commit()
    finally:
        session.close()

    suggestions = optimization_service.get_optimization_suggestions(time_window_days=30)

    assert suggestions, "expected at least one optimization suggestion"
    suggestion = suggestions[0]
    assert suggestion["current_provider"] == CloudProviderEnum.AWS.value
    assert suggestion["recommended_provider"] == CloudProviderEnum.GCP.value
    assert suggestion["estimated_savings_percent"] >= 40.0
    assert suggestion["workload_id"].startswith("aws-account:Compute@us-east-1")
