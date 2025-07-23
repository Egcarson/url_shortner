from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import String, Integer, DateTime, Column, ForeignKey
from datetime import datetime
from typing import List, Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True, nullable=False)
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    username: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    email_address: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False), exclude=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))

    url: List["URL"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<User ID={self.id}, username={self.username}, email_address={self.email_address}>"

class URL(SQLModel, table=True):
    __tablename__ = "urls"

    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False))
    original_url: str = Field(sa_column=Column(String(255), nullable=False))
    short_code: str = Field(sa_column=Column(String(10), index=True, unique=True))
    user_id: Optional[int] = Field(sa_column=Column(ForeignKey("users.id"), nullable=True))
    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))
    expires_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    click_count: int = Field(sa_column=Column(Integer, default=0))
    is_active: bool = True

    user: Optional["User"] = Relationship(back_populates="url", sa_relationship_kwargs={"lazy": "selectin"})
    

class BlacklistedToken(SQLModel, table=True):
    __tablename__ = "blacklistedtokens"

    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False))
    token: str = Field(sa_column=Column(String, index=True, unique=True))
    expires_at: datetime