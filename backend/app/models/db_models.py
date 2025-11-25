from sqlalchemy import Column, DateTime, Integer, String, func

from ..db import Base


class TimestampMixin:
    """Reusable columns for basic auditing."""

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ExampleResource(TimestampMixin, Base):
    """Simple model to ensure metadata generation works."""

    __tablename__ = "example_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)


__all__ = ["ExampleResource", "TimestampMixin"]
