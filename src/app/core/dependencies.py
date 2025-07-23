from fastapi import Request, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from src.app.core.utils import verify_access_token
from src.app.db.main import get_session
from src.app.core.utils import is_token_blacklisted
from src.app.services import user_services


class AccessPass(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, session: AsyncSession=Depends(get_session)) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials
        
        try:
            token_data = verify_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
                )

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
                )

        if token_data.get('jti') is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token missing JTI (likely expired)"
                )

            
        if await is_token_blacklisted(token, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has been revoked"
                )

        
        self.verify_token_data(token_data)

        return token_data
    
    def verify_token_data(self, token_data):
        raise NotImplementedError("Override this method in child classes")


class AccessTokenBearer(AccessPass):
    
    def verify_token_data(self, token_data: dict):
        
        if token_data and token_data.get('refresh'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Access Token. Please provide a valid access_token"
            )

class RefreshTokenBearer(AccessPass):

    def verify_token_data(self, token_data: dict):

        if token_data and not token_data.get('refresh'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Refresh Token. Please provide a valid refresh_token"
            )


async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    
    user_email = token_details['user']['email']

    user = await user_services.get_user_by_email(user_email, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return user


refresh_token = RefreshTokenBearer()