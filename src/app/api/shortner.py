from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse, JSONResponse
from typing import List
from src.app.schemas import URLRead, URLCreate
from src.app.models import User
from src.app.core.dependencies import get_current_user
from src.app.db.main import get_session
from src.app.services import url_services, user_services
from datetime import datetime

url_router = APIRouter(
    tags=["URL Shortner"]
)


@url_router.post('/urls', status_code=status.HTTP_201_CREATED, response_model=URLRead)
async def create_short_url(
    url_data: URLCreate,
    current_user: User=Depends(get_current_user),
    session: AsyncSession=Depends(get_session)
    ):

    #checks if the short_code exists "i.e if it has been taken by another user"
    check_existing = await url_services.existing_short_code(url_data.short_code, session)
    
    if check_existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shortcode already exists. Please choose another or autogenerate."
        )
    
    #creates a new url short code
    new_url = await url_services.create_short_url(url_data, current_user, session)

    return new_url

@url_router.get('/urls', status_code=status.HTTP_200_OK, response_model=List[URLRead])
async def get_urls(
    current_user: User=Depends(get_current_user),
    session: AsyncSession=Depends(get_session)
    ):

    urls = await url_services.get_urls(current_user.id, session)

    return urls


@url_router.get('/urls/{short_code}', status_code=status.HTTP_200_OK)
async def redirect_to_original_url(
    short_code: str,
    session: AsyncSession=Depends(get_session)
    ):

    #checks if the short code is active or correct
    url = await url_services.existing_short_code(short_code, session)
    if not url or not url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortcode does not exist or no longer active."
        )
    
    if url.expires_at and url.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL expired."
        )
    
    await url_services.redirect_url(url.short_code, session)

    return RedirectResponse(str(url.original_url), status_code=status.HTTP_307_TEMPORARY_REDIRECT)
