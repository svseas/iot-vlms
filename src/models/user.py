"""User-related Pydantic models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.models.base import BaseSchema, TimestampMixin


class UserRole(str, Enum):
    """User roles for RBAC."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    TECHNICIAN = "technician"
    VIEWER = "viewer"


# Request Models


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.VIEWER


class UserLoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None


class UserPasswordChangeRequest(BaseModel):
    """Request model for changing password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing access token."""

    refresh_token: str


# Response Models


class UserResponse(BaseSchema, TimestampMixin):
    """Response model for user data."""

    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool


class UserListResponse(BaseSchema):
    """Response model for user list item."""

    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # user_id
    email: str
    role: UserRole
    exp: datetime
    type: str
