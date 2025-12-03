"""SQLAlchemy ORM models."""

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from ..db import Base


class CloudProvider(Base):
    __tablename__ = "cloud_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
