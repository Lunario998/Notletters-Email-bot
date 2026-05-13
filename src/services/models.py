from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LetterBody(BaseModel):
    html: str = ""
    text: str = ""


class Letter(BaseModel):
    id: UUID
    sender: str
    sender_name: str
    subject: str
    letter: LetterBody = Field(default_factory=LetterBody)
    star: bool = False
    date: datetime


class ChangePasswordResult(BaseModel):
    email: str
    success: bool
    message: str


class LettersResult(BaseModel):
    email: str
    success: bool
    letters: list[Letter] = Field(default_factory=list)
    message: str | None = None
