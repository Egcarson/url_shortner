from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from src.app.db.main import get_session
from src.app.services import user_services
from src.app.schemas import User, UserUpdate


user_router = APIRouter(
    tags=["User"]
)

@user_router.get('/users', status_code=status.HTTP_200_OK, response_model=List[User])
async def get_users(skip: int=0, limit: int=10, session: AsyncSession = Depends(get_session)):

    users = await user_services.get_users(skip, limit, session)

    return users

@user_router.get('/users/{user_id}', status_code=status.HTTP_200_OK, response_model=User)
async def get_single_user(user_id: int, session: AsyncSession=Depends(get_session)):

    user = await user_services.get_user(user_id, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@user_router.put('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED, response_model=User)
async def update_user(user_id: int, user_data:UserUpdate, session: AsyncSession=Depends(get_session)):

    user_to_update = await user_services.get_user(user_id, session)

    if user_to_update is not None:

        try:
            user = await user_services.update_user(user_data, user_id, session)

            return user
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An error occured while trying to update this user"
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

@user_router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session:AsyncSession=Depends(get_session)):

    user_to_delete = await user_services.get_user(user_id, session)

    if user_to_delete is not None:

        try:
            await user_services.delete_user(user_id, session)
        
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An error occured while trying to update this user"
            )
    else:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )