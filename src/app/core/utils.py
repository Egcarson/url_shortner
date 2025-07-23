import jwt
import string
import logging
import secrets
from fastapi import HTTPException, status
from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from uuid import uuid4
from datetime import datetime, timedelta
from src.app.models import BlacklistedToken, URL
from src.app.core.config import Config

passwd_context = CryptContext(
    schemes=['bcrypt']
)

ACCESS_TOKEN_EXPIRTY = 3600

ALPHABET = string.ascii_letters + string.digits

async def generate_short_code(session: AsyncSession, length: int = 8):
    """
    Generates a cryptographically secure and unique short code.
    Checks the database if it already exists.
    """

    while True:
        code = ''.join(secrets.choice(ALPHABET) for _ in range(length))

        result = await session.execute(select(URL).where(URL.short_code == code))

        if not result.scalar_one_or_none():
            return code


def hashpassword(password: str) -> str:
    return passwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return passwd_context.verify(password, hashed_password)


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool=False):
    
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRTY))
    payload["jti"] = str(uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def verify_access_token(token: str) -> dict:
    try:
        token_data=jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )

        if 'jti' not in token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain 'jti'"
            )
        return token_data
        
    except jwt.ExpiredSignatureError:
        logging.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    except jwt.PyJWKError as e:
        logging.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def blacklist_token(token: str, session: AsyncSession):
    """
    Adds token to blacklist table models.BlacklistedToken
    Decodes tokens then blacklists it if token is valid
    """

    try:
        payload = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )

        exp_timestamp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp_timestamp)
    except Exception:
        raise ValueError("Invalid token")
    
    blacklist_token = BlacklistedToken(token=token, expires_at=expires_at)

    session.add(blacklist_token)
    await session.commit()


async def is_token_blacklisted(token: str, session: AsyncSession):
    """
    Returns blacklisted token from database.
    This function helps the logout endpoint
    """

    statement = select(BlacklistedToken).where(BlacklistedToken.token == token)

    result = await session.execute(statement)

    return result.scalar_one_or_none() is not None

async def delete_expired_tokens(session: AsyncSession):
    """
    Deletes expire token from models.BlacklistedToken (table)
    Done with BackgroundTask to enable efficient flow
    """
    
    now = datetime.now()
    token = delete(BlacklistedToken).where(BlacklistedToken.expires_at < now)
    await session.execute(token)
    await session.commit()