
from dash import html, dcc
import dash_bootstrap_components as dbc

from .filters import create_filters
from .kpi_cards import create_kpi_cards

def create_layout():
    """Создать основной макет приложения"""
    return html.Div([
        # Заголовок
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Малинка - Аналитический дашборд", 
                           className="text-center mb-2 text-primary"),
                    html.P("Интерактивная аналитика маркетплейса в реальном времени", 
                          className="text-center text-muted mb-4"),
                ], width=12)
            ])
        ], className="my-4"),
        
        # Фильтры
        create_filters(),
        
        # KPI карточки
        html.Div(id="kpi-cards-container"),
        
        # Графики
        dbc.Container([
            # Первый ряд
            dbc.Row([
                dbc.Col(dcc.Graph(id="sales-trend"), lg=6, className="mb-4"),
                dbc.Col(dcc.Graph(id="category-sales"), lg=6, className="mb-4"),
            ]),
            
            # Второй ряд
            dbc.Row([
                dbc.Col(dcc.Graph(id="funnel-chart"), lg=6, className="mb-4"),
                dbc.Col(dcc.Graph(id="segmentation-chart"), lg=6, className="mb-4"),
            ]),
            
            # Третий ряд
            dbc.Row([
                dbc.Col(dcc.Graph(id="ad-performance"), lg=6, className="mb-4"),
                dbc.Col(dcc.Graph(id="returns-analysis"), lg=6, className="mb-4"),
            ]),
            
            # Четвертый ряд
            dbc.Row([
                dbc.Col(dcc.Graph(id="traffic-channels"), lg=6, className="mb-4"),
                dbc.Col(dcc.Graph(id="inventory-status"), lg=6, className="mb-4"),
            ]),
            
            # Пятый ряд
            dbc.Row([
                dbc.Col(dcc.Graph(id="support-metrics"), lg=6, className="mb-4"),
                dbc.Col(dcc.Graph(id="supplier-performance"), lg=6, className="mb-4"),
            ]),
        ], fluid=True),
        
        # Скрытые элементы для хранения данных
        dcc.Store(id="data-store"),
        dcc.Interval(id="interval-component", interval=300000, n_intervals=0),  # Обновление каждые 5 минут
    ])