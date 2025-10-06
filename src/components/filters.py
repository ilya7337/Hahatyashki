from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_filters():
    """Создать панель фильтров"""
    # Дата по умолчанию - последние 30 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Период анализа", className="form-label"),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=start_date.date(),
                        end_date=end_date.date(),
                        display_format='YYYY-MM-DD',
                        className="w-100"
                    ),
                ], lg=3, md=6, className="mb-3"),
                
                dbc.Col([
                    html.Label("Категория товаров", className="form-label"),
                    dcc.Dropdown(
                        id='category-filter',
                        options=[{'label': 'Все категории', 'value': 'all'}],
                        value='all',
                        clearable=False,
                        className="w-100"
                    ),
                ], lg=3, md=6, className="mb-3"),
                
                dbc.Col([
                    html.Label("Сегмент пользователей", className="form-label"),
                    dcc.Dropdown(
                        id='segment-filter',
                        options=[{'label': 'Все сегменты', 'value': 'all'}],
                        value='all',
                        clearable=False,
                        className="w-100"
                    ),
                ], lg=3, md=6, className="mb-3"),
                
                dbc.Col([
                    html.Label("Канал трафика", className="form-label"),
                    dcc.Dropdown(
                        id='channel-filter',
                        options=[{'label': 'Все каналы', 'value': 'all'}],
                        value='all',
                        clearable=False,
                        className="w-100"
                    ),
                ], lg=3, md=6, className="mb-3"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button("Применить фильтры", id="apply-filters", color="primary", className="w-100"),
                ], lg=2, className="mb-3"),
                
                dbc.Col([
                    dbc.Button("Сбросить фильтры", id="reset-filters", color="outline-secondary", className="w-100"),
                ], lg=2, className="mb-3"),
            ], justify="start"),
        ])
    ], className="mb-4")