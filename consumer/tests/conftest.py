# Standard imports
import sqlite3

import pytest


@pytest.fixture(scope="session")
def db():
    """Fixture to set up the in-memory database with test data"""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS site (
    	id int NOT null PRIMARY KEY,
    	url text NULL,
    	current_up_status varchar NOT null,
        last_update timestamp NOT NULL
    )"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ping_status (
        id  SERIAL PRIMARY KEY,
        site_id int,
        up_status varchar NOT NULL,
        created_at timestamp NOT NULL,
        response_time float4 NOT NULL,
        response_code varchar NULL,
        response_header text NULL,
        response text NULL,
        CONSTRAINT fk_site FOREIGN KEY(site_id) REFERENCES site(id) ON DELETE SET NULL
    )"""
    )
    yield conn
