from fastapi import Depends, HTTPException
from schemas import UserCreate, UserBase, UserPublic, UserPrivate, Token
from typing import Annotated
from database import get_db
from sqlalchemy import select
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func

from auth import (
    create_access_token,
    oauth2_scheme,
    verify_password,
    hash_password,
    CurrentUser,
)
from config import settings

# from sqlalchemy.orm import
import models


router = APIRouter()


@router.get(
    "",
    response_model=list[UserPublic],
    status_code=status.HTTP_200_OK,
)
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User))
    return result.scalars().all()


@router.post(
    "",
    response_model=UserPrivate,
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
        password_hash=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivate)
async def get_me(current_user: CurrentUser):
    """Get the currently authenticated user."""
    return current_user


@router.patch("/me", response_model=UserPrivate)
async def update_me(
    current_user: CurrentUser,
    data: UserBase,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update the currently authenticated user's profile."""
    # Check if new username is already taken (only if changed)
    if data.username != current_user.username:
        existing_username = await db.execute(
            select(models.User).where(models.User.username == data.username)
        )
        if existing_username.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Check if new email is already taken (only if changed)
    if data.email != current_user.email:
        existing_email = await db.execute(
            select(models.User).where(models.User.email == data.email)
        )
        if existing_email.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    current_user.username = data.username
    current_user.email = data.email

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete the currently authenticated user."""
    await db.delete(current_user)
    await db.commit()
    return {"message": "User deleted successfully"}


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: int,
    data: UserBase,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a user (owner only)."""
    # Enforce ownership
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another user's profile",
        )

    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.username = data.username
    user.email = data.email

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a user (owner only)."""
    # Enforce ownership
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's profile",
        )

    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
