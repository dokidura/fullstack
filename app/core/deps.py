# app/core/deps.py
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.core.user_store import fake_users_db
from app.models.schemas import UserResponse

security = HTTPBearer()

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "student": {
        "submission:create",
        "submission:read_own",
        "submission:read_one_own",
        "ai:read_result_own",
        "gradebook:read_own",
    },
    "teacher": {
        "submission:read_all",
        "submission:update",
        "ai:process",
        "ai:read_result_all",
        "gradebook:read_all",
        "gradebook:export",
        "user:role_manage",
    },
}


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserResponse:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if not email:
            raise _credentials_exception()
    except JWTError:
        raise _credentials_exception()

    user = fake_users_db.get(email)
    if user is None:
        raise _credentials_exception()

    return UserResponse(**user)


def require_role(role: str):
    def role_checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions",
            )
        return current_user

    return role_checker


def require_permission(permission: str):
    def checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        perms = ROLE_PERMISSIONS.get(current_user.role, set())
        if permission not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return checker


def require_teacher():
    return require_role("teacher")


def require_admin():
    def checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if current_user.role != "teacher" or current_user.email not in settings.ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins only",
            )
        return current_user

    return checker
