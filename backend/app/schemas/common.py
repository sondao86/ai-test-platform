from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TimestampMixin(BaseModel):
    created_at: datetime


class UUIDMixin(BaseModel):
    id: UUID


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
