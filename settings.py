from enum import Enum
from pydantic import BaseModel

DEFAULT_TIMEOUT = 30

# kafka settings
BOOTSTRAP_SERVERS = ['localhost:9092']
SITE_CONSUMER_TOPIC = "site-consumer"
SITE_CONSUMER_GROUP = "site-group"
DB_CONSUMER_TOPIC = "db-consumer"
DB_CONSUMER_GROUP = "db-group"


class Schedule(Enum):
    EVERY_MINUTE = "run.every_minute"
    EVERY_FIVE_MINUTES = "run.every_five_minutes"
    EVERY_TEN_MINUTES = "run.every_ten_minutes"
    EVERY_HOUR = "run.every_hour"

class Endpoint(BaseModel): 
    id: int
    url: str
