from sqlmodel import create_engine, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.app.core.config import Config


async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL
    )
)


async def init_db() -> None:
    """
    This async function is for automatically creating table and pushing to postgress 
    at the start of the engine.

    Note: this does not push new tables (thats the work of alembic)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """
    This is an async generator function that creates and provides a database session.

    - It uses SQLAlchemy's `sessionmaker` to create a session factory bound to an async database engine.
    - `AsyncSession` is used to enable asynchronous DB operations.
    - `expire_on_commit=False` means data won't be cleared from the session after committing.
    - `async with Session() as session` ensures the session is properly opened and closed.
    - `yield session` allows other parts of your app (like FastAPI routes) to use this session for DB operations.
    """
    Session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session