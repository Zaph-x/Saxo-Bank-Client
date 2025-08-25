import psycopg2
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None

    @staticmethod
    def setup():
        """
        Sets up the database and its tables.
        If the database does not exist, it will be created.
        If the tables do not exist, they will be created.
        This method should be called before any other database operations.
        """
        with Database() as db:
            db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                context_id VARCHAR(255) NOT NULL,
                reference_id VARCHAR(255) NOT NULL,
                algo_name VARCHAR(255) NOT NULL,
                uic INTEGER NOT NULL,
                timeframe INTEGER NOT NULL DEFAULT 1000,
                asset_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Database setup completed.")

    def __enter__(self):
        logger.debug(f"Establishing database connection... {os.getenv('POSTGRES_USER')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}")
        self.connection = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT', '5432')
            )
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                logger.error("An error occurred, rolling back the transaction.", exc_info=(exc_type, exc_value, traceback))
                self.connection.rollback()
            self.connection.close()

    def execute(self, query, params=None):
        if params is None:
            params = ()
        if self.cursor is None:
            raise RuntimeError("Database connection is not established.")
        self.cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            return self.cursor.fetchall()
        return None

