from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db import Base, engine


class CloudAccount(Base):
    __tablename__ = "cloud_accounts"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(255), nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_identifier = Column(String(255), nullable=False, unique=True)
    tags = Column(JSON, nullable=True)

    cost_records = relationship(
        "CostRecordDB",
        back_populates="account",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    performance_records = relationship(
        "PerformanceRecordDB",
        back_populates="account",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class CostRecordDB(Base):
    __tablename__ = "cost_records"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(255), nullable=False, index=True)
    account_id = Column(
        Integer,
        ForeignKey("cloud_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    usage_amount = Column(Float, nullable=False)
    usage_unit = Column(String(64), nullable=False)
    cost_amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    account = relationship("CloudAccount", back_populates="cost_records")


class PerformanceRecordDB(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(255), nullable=False, index=True)
    account_id = Column(
        Integer,
        ForeignKey("cloud_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_id = Column(String(255), nullable=False)
    service = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    cpu_utilization = Column(Float, nullable=False)
    memory_utilization = Column(Float, nullable=False)
    network_io = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    account = relationship("CloudAccount", back_populates="performance_records")


def create_all_tables() -> None:
    """Create all database tables defined in this module."""
    Base.metadata.create_all(bind=engine)


__all__ = [
    "CloudAccount",
    "CostRecordDB",
    "PerformanceRecordDB",
    "create_all_tables",
]
