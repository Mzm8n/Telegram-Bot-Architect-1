from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: str):
        async_url = url.replace("postgresql://", "postgresql+asyncpg://")
        if not async_url.startswith("postgresql+asyncpg://"):
            async_url = f"postgresql+asyncpg://{url.split('://')[-1]}"
        
        self.engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def close(self) -> None:
        await self.engine.dispose()


db: Database | None = None


async def init_database(url: str) -> Database:
    global db
    db = Database(url)
    return db


async def get_db() -> Database:
    if db is None:
        raise RuntimeError("Database not initialized")
    return db
