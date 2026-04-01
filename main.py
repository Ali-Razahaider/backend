from fastapi import FastAPI, Depends, HTTPException
from schemas import UserCreate, UserBase, PostCreate, UserResponse
from typing import Annotated
from database import get_db, Base, engine
from sqlalchemy import select
from fastapi import status
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm import
import models


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return "hello world"


@app.get(
    "/api/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User))
    return result.scalars().all()


@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    user_name = result.scalars().first()
    if user_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        # password_hash=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
