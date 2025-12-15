"""Base models for API request/response."""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields."""

    created_at: datetime
    updated_at: datetime | None = None


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    limit: int = 20

    @property
    def offset(self) -> int:
        """Calculate offset for SQL query."""
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    """Pagination metadata for responses."""

    page: int
    limit: int
    total: int
    has_more: bool


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    success: bool = True
    data: T
    meta: dict[str, Any] | None = None


class ApiListResponse(BaseModel, Generic[T]):
    """Standard API list response with pagination."""

    success: bool = True
    data: list[T]
    meta: PaginationMeta


class ApiErrorDetail(BaseModel):
    """Error detail structure."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiErrorResponse(BaseModel):
    """Standard API error response."""

    success: bool = False
    error: ApiErrorDetail


class IDResponse(BaseModel):
    """Response containing only an ID."""

    id: UUID


class MessageResponse(BaseModel):
    """Response containing only a message."""

    message: str
