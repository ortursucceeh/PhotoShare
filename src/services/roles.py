from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, UserRoleEnum
from src.services.auth import auth_service


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")
