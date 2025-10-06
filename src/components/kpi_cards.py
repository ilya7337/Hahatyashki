from dash import html
import dash_bootstrap_components as dbc
from typing import Dict, Any

def create_kpi_card(title: str, value: str, delta: str = None, delta_color: str = "success") -> dbc.Card:
    """Создать карточку KPI с метрикой"""
    delta_element = []
    if delta:
        delta_icon = "↗️" if delta_color == "success" else "↘️"
        delta_element = [
            dbc.CardFooter([
                html.Span(f"{delta_icon} {delta}", className=f"text-{delta_color}")
            ])
        ]
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-title text-muted"),
            html.H3(value, className="card-text fw-bold"),
        ]),
        *delta_element
    ], className="text-center h-100")

def create_kpi_cards(kpi_data: Dict[str, Any]) -> dbc.Row:
    """Создать ряд KPI карточек"""
    return dbc.Row([
        dbc.Col(create_kpi_card(
            "💰 Общая выручка", 
            kpi_data.get('total_revenue', '0 ₽'),
            kpi_data.get('revenue_delta'),
            kpi_data.get('revenue_delta_color', 'success')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "📦 Количество заказов", 
            kpi_data.get('total_orders', '0'),
            kpi_data.get('orders_delta'),
            kpi_data.get('orders_delta_color', 'success')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "🛒 Средний чек", 
            kpi_data.get('avg_order_value', '0 ₽'),
            kpi_data.get('aov_delta'),
            kpi_data.get('aov_delta_color', 'success')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "🔄 Уровень возвратов", 
            kpi_data.get('return_rate', '0%'),
            kpi_data.get('returns_delta'),
            kpi_data.get('returns_delta_color', 'danger')
        ), lg=3, md=6, className="mb-3"),
    ], className="g-3")