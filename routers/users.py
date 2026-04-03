from fastapi import Depends, HTTPException
from schemas import (
    UserCreate,
    UserBase,
    UserResponse,
)
from typing import Annotated
from database import get_db
from sqlalchemy import select
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

# from sqlalchemy.orm import
import models


router = APIRouter()


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_202_ACCEPTED,
)
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User))
    return result.scalars().all()


@router.post(
    "",
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


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, data: UserBase, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesnt Exist"
        )
    else:
        user.username = data.username
        user.email = data.email

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found "
        )
    await db.delete(user)
    await db.commit()
