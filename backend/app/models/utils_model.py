from sqlmodel import Field, SQLModel


class Message(SQLModel):
    message: str = Field(max_length=255)
