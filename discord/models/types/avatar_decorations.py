from pydantic import BaseModel

from .snowflake import Snowflake


class AvatarDecorationData(BaseModel):
    asset: str
    sku_id: Snowflake
