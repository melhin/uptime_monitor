from consumer.db_consumer import consume_db_writer
from consumer.db_consumer import consume_db_writer
from consumer.db_conn import connection, create_initial_tables_if_not_exist

if __name__ == "__main__":
    create_initial_tables_if_not_exist(connection=connection)
    consume_db_writer()
