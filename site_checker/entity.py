
from enum import Enum

from pydantic import BaseModel


class Schedule(Enum):
    EVERY_MINUTE = "run.every_minute"
    EVERY_FIVE_MINUTES = "run.every_five_minutes"
    EVERY_TEN_MINUTES = "run.every_ten_minutes"
    EVERY_HOUR = "run.every_hour"


class Endpoint(BaseModel): 
    id: int
    url: str
