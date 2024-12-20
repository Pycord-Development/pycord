from pydantic import BaseModel

from .user import User


class Ban(BaseModel):
    reason: str
    user: User
