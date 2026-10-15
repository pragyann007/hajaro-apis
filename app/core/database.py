from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# create engine 
engine = create_async_engine(settings.DATABASE_URL,echo=True,future=True)
AsyncSessionMaker = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
class Base(DeclarativeBase):
    pass

async def get_db()->AsyncSession:
    async with AsyncSessionMaker() as session :
        yield session

