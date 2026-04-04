from pydantic import Field, BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):

    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class UserPrivate(UserPublic):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class PostBase(BaseModel):
    title: str = Field(min_length=5)
    content: str = Field(min_length=10)
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    author: UserPublic
