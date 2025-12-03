"""Pydantic schemas that define API contracts."""

from pydantic import BaseModel


class CloudProviderBase(BaseModel):
    name: str
    description: str | None = None


class CloudProviderCreate(CloudProviderBase):
    pass


class CloudProviderRead(CloudProviderBase):
    id: int

    class Config:
        orm_mode = True
