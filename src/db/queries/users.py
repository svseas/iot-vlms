"""User database queries."""

from uuid import UUID

import asyncpg

from src.core.database import fetch, fetchrow, execute


async def get_user_by_id(user_id: UUID) -> asyncpg.Record | None:
    """Get a user by ID."""
    return await fetchrow(
        """
        SELECT id, email, password_hash, full_name, role, is_active,
               allowed_regions, metadata, created_at, updated_at
        FROM users
        WHERE id = $1
        """,
        user_id,
    )


async def get_user_by_email(email: str) -> asyncpg.Record | None:
    """Get a user by email."""
    return await fetchrow(
        """
        SELECT id, email, password_hash, full_name, role, is_active,
               allowed_regions, metadata, created_at, updated_at
        FROM users
        WHERE email = $1
        """,
        email,
    )


async def create_user(
    email: str,
    password_hash: str,
    full_name: str,
    role: str = "viewer",
) -> asyncpg.Record:
    """Create a new user."""
    return await fetchrow(
        """
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES ($1, $2, $3, $4)
        RETURNING id, email, full_name, role, is_active, created_at, updated_at
        """,
        email,
        password_hash,
        full_name,
        role,
    )


async def update_user(
    user_id: UUID,
    email: str | None = None,
    full_name: str | None = None,
) -> asyncpg.Record | None:
    """Update user profile."""
    updates = []
    params = []
    param_idx = 1

    if email is not None:
        updates.append(f"email = ${param_idx}")
        params.append(email)
        param_idx += 1

    if full_name is not None:
        updates.append(f"full_name = ${param_idx}")
        params.append(full_name)
        param_idx += 1

    if not updates:
        return await get_user_by_id(user_id)

    params.append(user_id)
    query = f"""
        UPDATE users
        SET {", ".join(updates)}
        WHERE id = ${param_idx}
        RETURNING id, email, full_name, role, is_active, created_at, updated_at
    """
    return await fetchrow(query, *params)


async def update_password(user_id: UUID, password_hash: str) -> bool:
    """Update user password."""
    result = await execute(
        """
        UPDATE users
        SET password_hash = $1
        WHERE id = $2
        """,
        password_hash,
        user_id,
    )
    return result == "UPDATE 1"


async def list_users(
    limit: int = 20,
    offset: int = 0,
    role: str | None = None,
    is_active: bool | None = None,
) -> list[asyncpg.Record]:
    """List users with optional filters."""
    conditions = []
    params = []
    param_idx = 1

    if role is not None:
        conditions.append(f"role = ${param_idx}")
        params.append(role)
        param_idx += 1

    if is_active is not None:
        conditions.append(f"is_active = ${param_idx}")
        params.append(is_active)
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    params.extend([limit, offset])
    query = f"""
        SELECT id, email, full_name, role, is_active, created_at
        FROM users
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    return await fetch(query, *params)


async def count_users(
    role: str | None = None,
    is_active: bool | None = None,
) -> int:
    """Count users with optional filters."""
    from src.core.database import fetchval

    conditions = []
    params = []
    param_idx = 1

    if role is not None:
        conditions.append(f"role = ${param_idx}")
        params.append(role)
        param_idx += 1

    if is_active is not None:
        conditions.append(f"is_active = ${param_idx}")
        params.append(is_active)
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"SELECT COUNT(*) FROM users {where_clause}"
    return await fetchval(query, *params)


async def deactivate_user(user_id: UUID) -> bool:
    """Deactivate a user."""
    result = await execute(
        """
        UPDATE users
        SET is_active = FALSE
        WHERE id = $1
        """,
        user_id,
    )
    return result == "UPDATE 1"


async def check_email_exists(email: str, exclude_user_id: UUID | None = None) -> bool:
    """Check if email is already in use."""
    from src.core.database import fetchval

    if exclude_user_id:
        return await fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1 AND id != $2)",
            email,
            exclude_user_id,
        )
    return await fetchval(
        "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)",
        email,
    )
