from fastapi import FastAPI, Depends, HTTPException
from schemas import UserCreate, UserBase, PostCreate, UserResponse, PostResponse
from typing import Annotated
from database import get_db, Base, engine
from sqlalchemy import select
from fastapi import status
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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


@app.patch("/api/users/{user_id}", response_model=UserResponse)
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


@app.delete("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found "
        )
    await db.delete(user)
    await db.commit()


@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author))
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No posts found"
        )
    else:
        return result.scalars().all()


@app.get("/api/posts/{post_id}")
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(selectinload(models.Post.author))
    )

    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No post exists"
        )
    else:
        return post


@app.post("/api/posts/", response_model=PostResponse)
async def create_post(
    new_post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.User).where(models.User.id == new_post.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesnt exist"
        )
    post = models.Post(
        title=new_post.title, content=new_post.content, user_id=new_post.user_id
    )

    db.add(post)
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post
