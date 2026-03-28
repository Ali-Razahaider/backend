from fastapi import FastAPI, Depends, HTTPException
from schemas import UserCreate, UserBase, PostBase, UserResponse
from typing import Annotated
from database import AsyncSession, get_db
from sqlalchemy import select
from fastapi import status

# from sqlalchemy.orm import
import models

app = FastAPI()


@app.get("/")
def home():
    return "hello world"


@app.get(
    "/api/users",
    response_model=list[UserBase],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User))
    return result.scalars().all()


@app.post("/api/users", response_model=UserResponse)
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
    existing_email = result.scalars().all()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    return new_user
