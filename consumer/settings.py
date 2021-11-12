import os

POSTGRESS_DB = os.environ.get("POSTGRESS_DB", "test_db")
POSTGRESS_HOST = os.environ.get("POSTGRESS_HOST", "localhost")
POSTGRESS_USER = os.environ.get("POSTGRESS_USER", "postgres")
POSTGRESS_PASSWORD = os.environ.get("POSTGRESS_PASSWORD", "postgres")
POSTGRESS_PORT = os.environ.get("POSTGRESS_PORT", 5432)

BOOTSTRAP_SERVERS = ['localhost:9092']
DB_CONSUMER_TOPIC = "db-consumer"
DB_CONSUMER_GROUP = "db-group"
