from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_date_filter():
    """Создать фильтр по дате"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    return html.Div([
        html.Label("📅 Период анализа", className="form-label"),
        dcc.DatePickerRange(
            id='date-range',
            start_date=start_date,
            end_date=end_date,
            display_format='YYYY-MM-DD',
            style={'width': '100%'}
        ),
    ])

def create_basic_filters():
    """Создать базовые фильтры"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_date_filter(), lg=6, md=12, className="mb-3"),
                dbc.Col([
                    html.Label("Категория", className="form-label"),
                    dcc.Dropdown(
                        id='basic-category-filter',
                        options=[{'label': 'Все категории', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=6, md=12, className="mb-3"),
            ]),
        ])
    ], className="mb-4")