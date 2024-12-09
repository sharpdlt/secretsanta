from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column
from typing import List, Optional
from pydantic import BaseModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str
    wishlist: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    no_wishlist: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    city_id: int = Field(foreign_key="city.id")
    city: "City" = Relationship(back_populates="users")

    def __str__(self):
        return self.full_name


class UserPair(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    giver_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")


class UserCreate(BaseModel):
    full_name: str
    email: str
    wishlist: List[str]
    no_wishlist: List[str]
    city_id: int

    class ConfigDict:
        arbitrary_types_allowed = True


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    wishlist: List[str]
    no_wishlist: List[str]

    class ConfigDict:
        arbitrary_types_allowed = True


class UserLogin(BaseModel):
    username: str
    password: str
