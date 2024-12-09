from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from typing import List


class City(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    users: List["User"] = Relationship(back_populates="city")
    description: str = Field(default="")


class CityCreate(BaseModel):
    name: str
    description: str

    class ConfigDict:
        arbitrary_types_allowed = True


class CityOut(BaseModel):
    id: int
    name: str
    description: str

    class ConfigDict:
        arbitrary_types_allowed = True
