"""SQLAlchemy ORM models for core multicloud entities."""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import relationship

from backend.app.db import Base, engine


class CloudAccount(Base):
    """Cloud account metadata shared by both cost and performance records."""

    __tablename__ = "cloud_accounts"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_identifier = Column(String(255), unique=True, nullable=False)
    tags = Column(JSON, nullable=True)

    cost_records = relationship(
        "CostRecordDB",
        back_populates="account",
        cascade="all, delete-orphan",
    )
    performance_records = relationship(
        "PerformanceRecordDB",
        back_populates="account",
        cascade="all, delete-orphan",
    )


class CostRecordDB(Base):
    """Persisted cost record aligned with `CostRecord` schema."""

    __tablename__ = "cost_records"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    account_id = Column(
        Integer,
        ForeignKey("cloud_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    service = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    usage_amount = Column(Float, nullable=False)
    usage_unit = Column(String(50), nullable=False)
    cost_amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    account = relationship("CloudAccount", back_populates="cost_records")


class PerformanceRecordDB(Base):
    """Persisted performance record aligned with `PerformanceRecord` schema."""

    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    account_id = Column(
        Integer,
        ForeignKey("cloud_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    resource_id = Column(String(255), nullable=False)
    service = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    cpu_utilization = Column(Float, nullable=False)
    memory_utilization = Column(Float, nullable=False)
    network_io = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    account = relationship("CloudAccount", back_populates="performance_records")


def create_all_tables() -> None:
    """Create all SQLAlchemy tables for the configured engine."""
    Base.metadata.create_all(bind=engine)
