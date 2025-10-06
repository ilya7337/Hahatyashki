from dash import html, dcc
import dash_bootstrap_components as dbc

from .navigation import create_navigation
from .pages import (
    create_home_layout,
    create_business_sales_layout,
    create_customer_behavior_layout,
    create_advertising_marketing_layout,
    create_service_quality_layout
)

def create_layout():
    """Создать основной макет приложения с multi-page navigation"""
    return html.Div([
        dcc.Location(id='url', refresh=False),
        create_navigation(),
        
        html.Div(id='page-content', style={
            'minHeight': 'calc(100vh - 80px)',
            'backgroundColor': '#f8f9fa',
            'padding': '20px 0'
        }),
        
        # Скрытые элементы
        dcc.Store(id='data-store'),
        dcc.Interval(id='interval-component', interval=300000, n_intervals=0),
    ])

def get_page_layout(pathname):
    """Получить layout для текущего пути"""
    if pathname == '/business-sales':
        return create_business_sales_layout()
    elif pathname == '/customer-behavior':
        return create_customer_behavior_layout()
    elif pathname == '/advertising-marketing':
        return create_advertising_marketing_layout()
    elif pathname == '/service-quality':
        return create_service_quality_layout()
    else:
        return create_home_layout()