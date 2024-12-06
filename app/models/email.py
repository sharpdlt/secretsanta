from sqlmodel import Field, SQLModel
from datetime import datetime


class EmailError(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    giver_email: str
    receiver_email: str
    error_message: str
    created_at: datetime = Field(default=datetime.utcnow)
