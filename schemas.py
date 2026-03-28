from pydantic import Field
from pydantic import BaseModel
from pydantic import EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class PostBase(BaseModel):
    title: str = Field(min_length=5)
    content: str = Field(min_length=100)
    published: bool = Field(True)
