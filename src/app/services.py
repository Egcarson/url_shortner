from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.app.schemas import UserCreate
from src.app.models import User, URL
from src.app.core.utils import hashpassword

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

        return result.all()