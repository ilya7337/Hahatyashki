import os
import logging
from dotenv import load_dotenv

load_dotenv()

import dash
from dash import Input, Output

from config import config
from src.components.layout import create_layout, get_page_layout
from src.components.filters import register_filter_callbacks
from src.components.pages.business_sales import register_business_callbacks
from src.components.pages.customer_behavior import register_customer_callbacks
from src.components.pages.advertising_marketing import register_advertising_callbacks
from src.components.pages.service_quality import register_service_callbacks

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if config.app.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Фабрика для создания приложения Dash"""
    
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        suppress_callback_exceptions=True
    )
    
    app.title = "Малинка Analytics"
    app.layout = create_layout()
    
    # Регистрация callback'ов
    register_callbacks(app)
    
    return app

def register_callbacks(app):
    """Зарегистрировать все callback'и приложения"""
    
    # Основной callback для навигации
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        """Отобразить страницу в зависимости от URL"""
        logger.info(f"Loading page: {pathname}")
        return get_page_layout(pathname)
    
    # Регистрируем callback'и для фильтров
    register_filter_callbacks(app)
    # Регистрируем callback'и для каждой страницы
    register_business_callbacks(app)
    register_customer_callbacks(app)
    register_advertising_callbacks(app)
    register_service_callbacks(app)

def main():
    """Основная функция запуска приложения"""
    try:
        app = create_app()
        
        logger.info("Starting Malinka Analytics application...")
        logger.info(f"Debug mode: {config.app.debug}")
        logger.info(f"Server will run on: {config.app.host}:{config.app.port}")
        
        app.run(
            debug=config.app.debug,
            host=config.app.host,
            port=config.app.port
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == '__main__':
    main()