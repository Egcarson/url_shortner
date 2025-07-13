from pydantic import BaseModel, SecretStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email_address: str

class UserCreate(UserBase):
    hashed_password: SecretStr

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str

class User(UserBase):
    id: int
    created_at: datetime.now


class URLCreate(BaseModel):
    original_url: str

class URL(BaseModel):
    id: int
    original_url: str
    short_code: str
    user_id: Optional[int] = None
    created_at: datetime
    expires_at: Optional[datetime] =None
    click_count: int