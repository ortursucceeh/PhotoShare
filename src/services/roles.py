from typing import List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, UserRoleEnum
from src.services.auth import auth_service


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRoleEnum]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and allows us to pass in arguments that will be used by other functions in our class.
        In this case, we are passing a list of allowed roles into our decorator.

        :param self: Represent the instance of the class
        :param allowed_roles: List[UserRoleEnum]: Define the allowed roles for this endpoint
        :return: None
        :doc-author: Trelent
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        # print(request.method)
        # print(request.url)
        # if request.method in ['POST', 'PUT', 'PATCH']:
        #     print(await request.json())
        # print('User', current_user.roles)
        # print('Roles', self.allowed_roles)
        """
        The __call__ function is the function that will be called when a user tries to access this endpoint.
        It takes in two parameters: request and current_user. The request parameter is an object containing information about the HTTP Request, such as its method (GET, POST, etc.) and URL.
        The current_user parameter is an object containing information about the currently logged-in user (if there is one). This value comes from our auth_service dependency.

        :param self: Refer to the class instance itself
        :param request: Request: Get the request object
        :param current_user: User: Get the user object from the auth_service
        :return: The decorated function
        :doc-author: Trelent
        """
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")
