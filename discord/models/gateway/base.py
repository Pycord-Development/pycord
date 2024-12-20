from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GatewayEvent(BaseModel, Generic[T]):
    op: int
    d: T
    s: int
    t: str
