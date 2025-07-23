from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.app.schemas import UserCreate, UserUpdate, URLCreate
from src.app.models import User, URL
from src.app.core.utils import hashpassword, generate_short_code
from datetime import datetime, timedelta

class UserService:


    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        
        user_dict = user_data.model_dump(exclude_unset=True)

        new_user = User(
            **user_dict
        )

        new_user.hashed_password = hashpassword(user_dict['hashed_password'])

        session.add(new_user)

        await session.commit()

        session.refresh(new_user)

        return new_user
    
    async def get_users(self, skip: int, limit: int, session: AsyncSession):

        statement = select(User).order_by(desc(User.created_at)).offset(skip).limit(limit)

        result = await session.execute(statement)

        return result.scalars().all()

    async def get_user_by_email(self, user_email, session: AsyncSession):

        statement = select(User).where(User.email_address == user_email)

        result = await session.execute(statement)

        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username, session: AsyncSession):

        statement = select(User).where(User.username == username)

        result = await session.execute(statement)

        return result.scalar_one_or_none()
    
    async def get_username(self, username: str, email: str, session: AsyncSession):

        user = await self.get_user_by_email(email, session)
        if user:
            return user
        
        return await self.get_user_by_username(username, session)
    
    async def get_user(self, user_id: int, session: AsyncSession):
        
        statement = select(User).where(User.id == user_id)

        result = await session.execute(statement)

        return result.scalar_one_or_none()
    
    async def update_user(self, user_data: UserUpdate, user_id: int, session: AsyncSession):

        user_to_update = await self.get_user(user_id, session)
        if user_to_update is not None:

            user_dict = user_data.model_dump(exclude_unset=True)

            for k, v in user_dict.items():
                setattr(user_to_update, k, v)

            await session.commit()

            return user_to_update
        else:
            return None
        
    
    async def delete_user(self, user_id: int, session: AsyncSession):

        user_to_delete = await self.get_user(user_id, session)

        if user_to_delete is not None:

            await session.delete(user_to_delete)

            await session.commit()
        
        else:
            return None


class URLService:

    async def existing_short_code(self, code: str, session: AsyncSession):

        statement = select(URL).where(URL.short_code == code)

        result = await session.execute(statement)

        return result.scalar_one_or_none()
    
    async def get_urls(self, current_user: int, session: AsyncSession):
        statement = select(URL).where(URL.user_id == current_user).order_by(desc(URL.created_at))

        result = await session.execute(statement)

        return result.scalars().all()

    async def create_short_url(self, url_data: URLCreate, current_user: User, session: AsyncSession) -> str:
        EXPIRY = 2
        url_expiry = datetime.now() + timedelta(days=EXPIRY)

        if url_data.short_code:
            existing = await self.existing_short_code(url_data.short_code, session)
            if existing:
                return None
            
            short_code = url_data.short_code
        
        else:
            short_code = await generate_short_code(session)
        
        new_url = URL(
            original_url=str(url_data.original_url),
            short_code=short_code,
            user_id=current_user.id,
            expires_at=url_expiry
        )
        
        session.add(new_url)
        await session.commit()
        await session.refresh(new_url)

        return new_url
    
    async def redirect_url(self, short_code: str, session: AsyncSession):

        url = await self.existing_short_code(short_code, session)

        #tracks how many times the link will be clicked
        url.click_count += 1

        session.add(url)
        await session.commit()

        return url



user_services = UserService()
url_services = URLService()