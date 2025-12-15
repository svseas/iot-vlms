"""User service for authentication and user management."""

import logging
from uuid import UUID

from src.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from src.db.queries import users as user_queries
from src.models.user import (
    TokenResponse,
    UserListResponse,
    UserPasswordChangeRequest,
    UserRegisterRequest,
    UserResponse,
    UserRole,
    UserUpdateRequest,
)

logger = logging.getLogger(__name__)


async def register_user(request: UserRegisterRequest) -> UserResponse:
    """Register a new user."""
    if await user_queries.check_email_exists(request.email):
        raise ConflictError(f"Email '{request.email}' is already registered")

    password_hash = hash_password(request.password)
    user = await user_queries.create_user(
        email=request.email,
        password_hash=password_hash,
        full_name=request.full_name,
        role=request.role.value,
    )

    logger.info("User registered", extra={"user_id": str(user["id"]), "email": request.email})

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=UserRole(user["role"]),
        is_active=user["is_active"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


async def authenticate_user(email: str, password: str) -> TokenResponse:
    """Authenticate a user and return tokens."""
    user = await user_queries.get_user_by_email(email)
    if not user:
        raise AuthenticationError("Invalid email or password")

    if not user["is_active"]:
        raise AuthenticationError("Account is deactivated")

    if not verify_password(password, user["password_hash"]):
        raise AuthenticationError("Invalid email or password")

    token_data = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    logger.info("User authenticated", extra={"user_id": str(user["id"])})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Refresh an access token using a refresh token."""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise AuthenticationError("Invalid or expired refresh token")

    user_id = UUID(payload["sub"])
    user = await user_queries.get_user_by_id(user_id)
    if not user:
        raise AuthenticationError("User not found")

    if not user["is_active"]:
        raise AuthenticationError("Account is deactivated")

    token_data = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
    }

    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


async def get_user(user_id: UUID) -> UserResponse:
    """Get a user by ID."""
    user = await user_queries.get_user_by_id(user_id)
    if not user:
        raise NotFoundError("User", user_id)

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=UserRole(user["role"]),
        is_active=user["is_active"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


async def update_user(user_id: UUID, request: UserUpdateRequest) -> UserResponse:
    """Update a user's profile."""
    if request.email:
        if await user_queries.check_email_exists(request.email, exclude_user_id=user_id):
            raise ConflictError(f"Email '{request.email}' is already in use")

    user = await user_queries.update_user(
        user_id=user_id,
        email=request.email,
        full_name=request.full_name,
    )

    if not user:
        raise NotFoundError("User", user_id)

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=UserRole(user["role"]),
        is_active=user["is_active"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


async def change_password(user_id: UUID, request: UserPasswordChangeRequest) -> None:
    """Change a user's password."""
    user = await user_queries.get_user_by_id(user_id)
    if not user:
        raise NotFoundError("User", user_id)

    if not verify_password(request.current_password, user["password_hash"]):
        raise ValidationError("Current password is incorrect")

    new_password_hash = hash_password(request.new_password)
    await user_queries.update_password(user_id, new_password_hash)

    logger.info("Password changed", extra={"user_id": str(user_id)})


async def list_users(
    page: int = 1,
    limit: int = 20,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> tuple[list[UserListResponse], int]:
    """List users with pagination and filters."""
    offset = (page - 1) * limit

    users = await user_queries.list_users(
        limit=limit,
        offset=offset,
        role=role.value if role else None,
        is_active=is_active,
    )

    total = await user_queries.count_users(
        role=role.value if role else None,
        is_active=is_active,
    )

    return [
        UserListResponse(
            id=u["id"],
            email=u["email"],
            full_name=u["full_name"],
            role=UserRole(u["role"]),
            is_active=u["is_active"],
            created_at=u["created_at"],
        )
        for u in users
    ], total


async def deactivate_user(user_id: UUID) -> None:
    """Deactivate a user account."""
    success = await user_queries.deactivate_user(user_id)
    if not success:
        raise NotFoundError("User", user_id)

    logger.info("User deactivated", extra={"user_id": str(user_id)})
