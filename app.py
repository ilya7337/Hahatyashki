import os
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

import dash
from dash import Dash
import dash_bootstrap_components as dbc

from config import config
from src.components.layout import create_layout
from src.components.callbacks import register_callbacks

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if config.app.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Фабрика для создания приложения Dash"""
    
    # Инициализация приложения с Bootstrap темой
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    
    # Конфигурация приложения
    app.title = "Малинка - Аналитический дашборд"
    app.layout = create_layout()
    
    # Регистрация callback'ов
    register_callbacks(app)
    
    return app

def main():
    """Основная функция запуска приложения"""
    try:
        app = create_app()
        
        logger.info("Starting Malinka Dashboard application...")
        logger.info(f"Debug mode: {config.app.debug}")
        logger.info(f"Server will run on: {config.app.host}:{config.app.port}")
        
        # Запуск приложения
        app.run(
            debug=config.app.debug,
            host=config.app.host,
            port=config.app.port,
            dev_tools_ui=config.app.debug,
            dev_tools_props_check=config.app.debug
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


main()