from dash import dcc, html, Output, Input, callback
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from src.database.queries.common import CHANNELS_QUERY, REGIONS_QUERY, CATEGORIES_QUERY, SEGMENTS_QUERY
import logging

logger = logging.getLogger(__name__)

def create_date_filter():
    """Создать фильтр по дате с предустановленными периодами"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    return html.Div([
        html.Label("📅 Период анализа", className="form-label"),
        
        # Выбор предустановленных периодов
        dcc.Dropdown(
            id='period-selector',
            options=[
                {'label': '🕐 Последние 24 часа', 'value': '1d'},
                {'label': '📅 Последние 7 дней', 'value': '7d'},
                {'label': '🗓️ Последние 30 дней', 'value': '30d'},
                {'label': '📊 Последние 90 дней', 'value': '90d'},
                {'label': '📈 Последний год', 'value': '365d'},
                {'label': '⏳ За все время', 'value': 'all'},
                {'label': '🎛️ Произвольный период', 'value': 'custom'}
            ],
            value='30d',
            clearable=False,
            className="mb-2"
        ),
        
        # Выбор дат (скрыт по умолчанию)
        html.Div([
            dcc.DatePickerRange(
                id='date-range',
                start_date=start_date,
                end_date=end_date,
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            ),
        ], id='date-range-container', style={'display': 'none'})
    ])

def create_issue_type_filter():
    """Фильтр по типу обращения, загружается через callback"""
    return html.Div([
        html.Label("📬 Тип обращения", className="form-label"),
        dcc.Dropdown(
            id='issue-type-filter',
            options=[],  # Загружается через callback
            value='all',
            placeholder="Все типы",
            clearable=False,
            className="mb-2"
        )
    ])

def create_segment_filter():
    """Фильтр по сегменту клиента"""
    return html.Div([
        html.Label("👥 Сегмент клиента", className="form-label"),
        dcc.Dropdown(
            id='service-segment-filter',
            options=[],  # Загружается через callback
            value='all',
            placeholder="Все сегменты",
            clearable=False,
            className="mb-2"
        )
    ])

def create_region_filter():
    """Фильтр по региону клиента"""
    return html.Div([
        html.Label("📍 Регион клиента", className="form-label"),
        dcc.Dropdown(
            id='service-region-filter',
            options=[],  # Загружается через callback
            value='all',
            placeholder="Все регионы",
            clearable=False,
            className="mb-2"
        )
    ])


def create_category_filter():
    """Создать фильтр категорий с загрузкой данных"""
    return html.Div([
        html.Label("📁 Категория", className="form-label"),
        dcc.Dropdown(
            id='basic-category-filter',
            options=[],  # Будет заполнено через callback
            value='all',
            clearable=False,
            placeholder="Все категории"
        ),
    ])

def create_supplier_filter():
    """Создать фильтр поставщиков с предустановленными опциями"""
    return html.Div([
        html.Label("🏭 Поставщик", className="form-label"),
        dcc.Dropdown(
            id='supplier-filter',
            options=[],
            value='all',
            clearable=False,
            placeholder="Все поставщики"
        ),
    ])

def create_channel_filter():
    """Создать фильтр каналов трафика"""
    return html.Div([
        html.Label("🌐 Канал", className="form-label"),
        dcc.Dropdown(
            id='channel-filter',
            options=[],  # Будет заполнено через callback
            value='all',
            clearable=False,
            placeholder="Загрузка каналов..."
        ),
    ])



# Callback'ы для работы с фильтрами
def register_filter_callbacks(app):
    """Зарегистрировать callback'ы для фильтров"""
    
    @app.callback(
        [Output('date-range-container', 'style'),
         Output('date-range', 'start_date'),
         Output('date-range', 'end_date')],
        [Input('period-selector', 'value')]
    )
    def update_date_range(period):
        """Обновить диапазон дат в зависимости от выбранного периода"""
        end_date = datetime.now().date()
        
        if period == 'custom':
            # Показываем выбор дат для произвольного периода
            start_date = end_date - timedelta(days=30)
            return {'display': 'block'}, start_date, end_date
        
        # Скрываем выбор дат для предустановленных периодов
        style = {'display': 'none'}
        
        if period == '1d':
            start_date = end_date - timedelta(days=1)
        elif period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        elif period == '365d':
            start_date = end_date - timedelta(days=365)
        elif period == 'all':
            # Для "За все время" устанавливаем широкий диапазон
            start_date = datetime(2025, 1, 1).date()  # Начало 2025 года
        else:  # 30d по умолчанию
            start_date = end_date - timedelta(days=30)
            
        return style, start_date, end_date
    
    def load_filter_options(query, default_label="Все"):
        """Вспомогательная функция для загрузки опций фильтра"""
        try:
            from src.database.connection import db_manager
            
            result = db_manager.execute_query(query)
            print(234)
            if not result.empty:
                column_name = result.columns[0]  # Получаем имя первой колонки
                options = [{'label': default_label, 'value': 'all'}]
                for _, row in result.iterrows():
                    options.append({
                        'label': row[column_name],
                        'value': row[column_name]
                    })
                logger.info(f"Loaded {len(options)} options from database")
                return options
            else:
                logger.warning(f"No data found for query: {query}")
                return [{'label': default_label, 'value': 'all'}]
                
        except Exception as e:
            return [{'label': default_label, 'value': 'all'}]
    
    @app.callback(
        Output('basic-category-filter', 'options'),
        [Input('app-load', 'children')],  # Триггер при загрузке приложения
        prevent_initial_call=False
    )
    def load_categories(trigger):
        """Загрузить категории из базы данных"""
        return load_filter_options(CATEGORIES_QUERY, "Все категории")
    
    # Загрузка сегментов
    @app.callback(
        Output('service-segment-filter', 'options'),
        Input('app-load', 'children'),
        prevent_initial_call=False
    )
    def load_segments(trigger):
        return load_filter_options(SEGMENTS_QUERY, "Все сегменты")
    
    # Загрузка типов обращений
    @app.callback(
        Output('issue-type-filter', 'options'),
        Input('app-load', 'children'),
        prevent_initial_call=False
    )
    def load_issue_types(trigger):
        query = "SELECT DISTINCT issue_type FROM customer_support WHERE issue_type IS NOT NULL ORDER BY issue_type"
        return load_filter_options(query, "Все типы")
    
    # Загрузка регионов
    @app.callback(
    Output('service-region-filter', 'options'),
    Input('app-load', 'children'),
    prevent_initial_call=False
    )
    def load_regions(trigger):
        """Загрузить регионы из user_segments"""
        return load_filter_options(REGIONS_QUERY, "Все регионы")
    
    @app.callback(
        Output('channel-filter', 'options'),
        [Input('app-load', 'children')],
        prevent_initial_call=False
    )
    def load_channels(trigger):
        """Загрузить каналы трафика"""
        return load_filter_options(CHANNELS_QUERY, "Все каналы")
    
    @callback(
    Output('supplier-filter', 'options'),
    [Input('app-load', 'children')]
)
    def load_suppliers(n_intervals):
        """Загрузить поставщиков из базы данных"""
        try:
            logger.info("Loading suppliers from database...")
            query = "SELECT DISTINCT supplier_name FROM suppliers WHERE supplier_name IS NOT NULL ORDER BY supplier_name"
            return load_filter_options(query, "Все поставщики")
        except Exception as e:
            logger.error(f"Error loading suppliers: {e}")
            return [{'label': 'Все поставщики', 'value': 'all'}]
    
    return app