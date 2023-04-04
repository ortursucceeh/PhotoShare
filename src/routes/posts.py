from src.services.roles import RoleChecker
from src.database.models import User, UserRoleEnum

# для визначення дозволу в залежності від ролі добавляємо списки дозволеності
allowed_get_posts = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_posts = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_update_posts = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_remove_posts = RoleChecker([UserRoleEnum.admin])


# в кожному маршруті добавляємо dependencies=[Depends(allowed_get_posts)] передаємо список тих кому дозволено

# @router.get("/", response_model=List[ResponseOwner], dependencies=[Depends(allowed_get_posts)])
# async def get_owners(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
#     owners = await repository_owners.get_owners(db)
#     return owners