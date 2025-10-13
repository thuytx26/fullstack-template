from sqlmodel import SQLModel, Field


class Message(SQLModel):
    message: str = Field(max_length=255)