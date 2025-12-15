"""API dependencies for dependency injection."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security import verify_access_token
from src.db.queries import users as user_queries
from src.models.user import UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """Get the current authenticated user from the JWT token."""
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = UUID(payload["sub"])
    user = await user_queries.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return dict(user)


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: UserRole):
    """Dependency to require specific roles."""

    async def role_checker(current_user: CurrentUser) -> dict:
        user_role = UserRole(current_user["role"])
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(r.value for r in roles)}",
            )
        return current_user

    return role_checker


AdminUser = Annotated[dict, Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))]
OperatorUser = Annotated[dict, Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR))]
TechnicianUser = Annotated[dict, Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.TECHNICIAN))]
