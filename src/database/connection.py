import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import pandas as pd

from config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Установить подключение к базе данных"""
        try:
            database_url = config.get_database_url()
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=config.app.debug
            )
            logger.info("Database connection established successfully")
            
            # Тестируем подключение
            self.test_connection()
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для работы с подключением"""
        connection = None
        try:
            connection = self.engine.connect()
            yield connection
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """Выполнить SQL запрос и вернуть DataFrame"""
        try:
            with self.get_connection() as conn:
                # Для PostgreSQL используем правильный формат параметров
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(text(query), conn)
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            return pd.DataFrame()
    
    def test_connection(self) -> bool:
        """Проверить подключение к базе данных"""
        try:
            with self.get_connection() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_table_info(self) -> pd.DataFrame:
        """Получить информацию о таблицах в базе данных"""
        try:
            query = """
            SELECT 
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return pd.DataFrame()

# Global database instance
db_manager = DatabaseManager()