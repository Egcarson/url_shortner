from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.schemas import UserCreate, LoginData
from src.app.services import user_services
from src.app.db.main import get_session
from src.app.core.utils import verify_password, create_access_token, blacklist_token, delete_expired_tokens
from src.app.core.dependencies import refresh_token, get_current_user
from src.app.models import User



auth_router = APIRouter(
    tags=["Authentication"]
)

REFRESH_EXPIRY = 1

@auth_router.get('/me', status_code=status.HTTP_200_OK)
async def get_current_user(c_user=Depends(get_current_user)):
    return c_user

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user_payload: UserCreate, session: AsyncSession = Depends(get_session)):

    user_email = user_payload.email_address

    existing_user = await user_services.get_user_by_email(user_email, session)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User already exists!"
        )
    
    new_user = await user_services.create_user(user_payload, session)

    return new_user

@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user_data: LoginData, session: AsyncSession=Depends(get_session)):

    username_or_emeail = user_data.username
    password = user_data.password
    
    user = await user_services.get_username(username_or_emeail, username_or_emeail, session)

    if user is not None:

        validate_password = verify_password(password, user.hashed_password)
        if validate_password:

            #create access_token
            access_token = create_access_token(
                user_data={
                    "username": user.username,
                    "email": user.email_address,
                    "user_id": user.id
                }
            )

            #create refresh_token
            refresh_token = create_access_token(
                user_data={
                    "username": user.username,
                    "email": user.email_address,
                    "user_id": user.id
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message": "User logged in successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user":{
                        "email": user.email_address,
                        "user_id": user.id
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid username or password"
    )


@auth_router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(token: str, bg_task: BackgroundTasks, session: AsyncSession=Depends(get_session)):
    try:
        await blacklist_token(token, session)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Token"
        )
    bg_task.add_task(delete_expired_tokens, session)
    
    return {"message": "Logged out successfully!"}

@auth_router.get('/access_token', status_code=status.HTTP_200_OK)
async def new_access_token(token_details: dict =Depends(refresh_token)):

    expiry = token_details['exp']

    if datetime.fromtimestamp(expiry, tz=timezone.utc) > datetime.now(timezone.utc):
        new_access_token = create_access_token(
            user_data=token_details['user']
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid refresh token"
    )