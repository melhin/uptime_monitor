import os

DEFAULT_TIMEOUT = 30

# kafka settings
BOOTSTRAP_SERVERS = ["localhost:9092"]
SITE_CONSUMER_TOPIC = "site-consumer"
SITE_CONSUMER_GROUP = "site-group"
DB_CONSUMER_TOPIC = "db-consumer"
DB_CONSUMER_GROUP = "db-group"

POOL_SIZE = 4


POSTGRESS_DB = os.environ.get("POSTGRESS_DB", "test_db")
POSTGRESS_HOST = os.environ.get("POSTGRESS_HOST", "localhost")
POSTGRESS_USER = os.environ.get("POSTGRESS_USER", "postgres")
POSTGRESS_PASSWORD = os.environ.get("POSTGRESS_PASSWORD", "postgres")
POSTGRESS_PORT = os.environ.get("POSTGRESS_PORT", 5432)
