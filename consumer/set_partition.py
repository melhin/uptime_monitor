import sys

from kafka import KafkaAdminClient
from kafka.admin import NewPartitions

import settings


def set_partitions(number: int):
    admin = KafkaAdminClient(bootstrap_servers=settings.BOOTSTRAP_SERVERS)
    admin.create_partitions({settings.DB_CONSUMER_TOPIC: NewPartitions(number)})


if __name__ == "__main__":
    set_partitions(int(sys.argv[1]))
