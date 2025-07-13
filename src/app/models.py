from sqlmodel import SQLModel, Field, Column, Relationship
from typing import Optional, List
from datetime import datetime



class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int = Field(primary_key=True, nullable=False)
    first_name: str
    last_name: str
    username: str
    email_address: str
    hashed_password: str = Field(exclude=True)
    created_at: datetime = Field(default=datetime.now())

    url: List["URL"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<User ID= {self.id}, username= {self.username}, email_address= {self.email_address}>"

class URL(SQLModel, table=True):
    __tablename__ = "url"

    id: int = Field(sa_column=Column(primary_key=True, nullable=False))
    original_url: str
    short_code: str = Field(sa_column=Column(index=True, unique=True))
    user_id: Optional[int] = None
    created_at: datetime = Field(default=datetime.now())
    expires_at: Optional[datetime] =None
    click_count: int = Field(default=0)

    user: Optional["User"] = Relationship(back_populates="url", sa_relationship_kwargs={"lazy": "selectin"})