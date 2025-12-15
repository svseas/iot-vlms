"""User API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.deps import AdminUser, CurrentUser
from src.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from src.models.base import (
    ApiListResponse,
    ApiResponse,
    MessageResponse,
    PaginationMeta,
)
from src.models.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserListResponse,
    UserLoginRequest,
    UserPasswordChangeRequest,
    UserRegisterRequest,
    UserResponse,
    UserRole,
    UserUpdateRequest,
)
from src.services.user import service as user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest):
    """Register a new user."""
    try:
        user = await user_service.register_user(request)
        return ApiResponse(data=user)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(request: UserLoginRequest):
    """Authenticate and get access tokens."""
    try:
        tokens = await user_service.authenticate_user(request.email, request.password)
        return ApiResponse(data=tokens)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        tokens = await user_service.refresh_access_token(request.refresh_token)
        return ApiResponse(data=tokens)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user(current_user: CurrentUser):
    """Get current user profile."""
    user = await user_service.get_user(UUID(str(current_user["id"])))
    return ApiResponse(data=user)


@router.patch("/me", response_model=ApiResponse[UserResponse])
async def update_current_user(request: UserUpdateRequest, current_user: CurrentUser):
    """Update current user profile."""
    try:
        user = await user_service.update_user(UUID(str(current_user["id"])), request)
        return ApiResponse(data=user)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/me/password", response_model=ApiResponse[MessageResponse])
async def change_password(request: UserPasswordChangeRequest, current_user: CurrentUser):
    """Change current user password."""
    try:
        await user_service.change_password(UUID(str(current_user["id"])), request)
        return ApiResponse(data=MessageResponse(message="Password changed successfully"))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("", response_model=ApiListResponse[UserListResponse])
async def list_users(
    _: AdminUser,
    page: int = 1,
    limit: int = 20,
    role: UserRole | None = None,
    is_active: bool | None = None,
):
    """List all users (admin only)."""
    users, total = await user_service.list_users(page, limit, role, is_active)
    return ApiListResponse(
        data=users,
        meta=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            has_more=(page * limit) < total,
        ),
    )


@router.get("/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(_: AdminUser, user_id: UUID):
    """Get a user by ID (admin only)."""
    try:
        user = await user_service.get_user(user_id)
        return ApiResponse(data=user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/{user_id}", response_model=ApiResponse[MessageResponse])
async def deactivate_user(_: AdminUser, user_id: UUID):
    """Deactivate a user (admin only)."""
    try:
        await user_service.deactivate_user(user_id)
        return ApiResponse(data=MessageResponse(message="User deactivated"))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
