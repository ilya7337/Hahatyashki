import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    ssl_mode: Optional[str] = None

@dataclass
class AppConfig:
    debug: bool
    host: str
    port: int
    secret_key: str

class Config:
    def __init__(self):
        # Database configuration
        self.db = DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'db'),
            user=os.getenv('DB_USER', 'haha'),
            password=os.getenv('DB_PASSWORD', '123456'),
            ssl_mode=os.getenv('DB_SSL_MODE', 'prefer')
        )
        
        # Application configuration
        self.app = AppConfig(
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', 8050)),
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key')
        )
        
        # Feature flags
        self.enable_cache = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
        self.cache_timeout = int(os.getenv('CACHE_TIMEOUT', 300))

    def get_database_url(self) -> str:
        """Получить DSN для подключения к PostgreSQL"""
        return f"postgresql://{self.db.user}:{self.db.password}@{self.db.host}:{self.db.port}/{self.db.database}"

# Global config instance
config = Config()