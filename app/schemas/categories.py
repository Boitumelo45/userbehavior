from pydantic import BaseModel
from typing_extensions import Literal


class Frequency(BaseModel):
    timeframe: Literal['daily', 'weekly', 'monthly'] = 'daily'

