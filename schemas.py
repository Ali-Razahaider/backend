from pydantic import Field, BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    pass
    # password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PostBase(BaseModel):
    title: str = Field(min_length=5)
    content: str = Field(min_length=100)
    published: bool = Field(True)


class PostCreate(BaseModel):
    user_id: int
