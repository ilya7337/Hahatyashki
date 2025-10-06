from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import logging

from src.database.connection import db_manager
from src.database.queries.business_sales import *
from src.components.kpi_cards import create_kpi_card
from src.components.charts import chart_builder
from src.components.filters import create_date_filter
from src.utils.data_processor import data_processor

logger = logging.getLogger(__name__)

def create_business_sales_layout():
    """Создать layout для страницы бизнес-аналитики"""
    return html.Div([
        # Заголовок страницы
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("💰 Бизнес-аналитика и продажи", 
                           style={'color': '#2C3E50', 'marginBottom': '10px'}),
                    html.P("Анализ продаж, выручки, поставщиков и складских запасов", 
                          style={'color': '#7F8C8D', 'marginBottom': '30px'}),
                ])
            ])
        ], fluid=True),
        
        # Фильтры
        create_business_filters(),
        
        # KPI карточки
        html.Div(id="business-kpi-cards", style={'marginBottom': '2rem'}),
        
        # Основные графики
        dbc.Container([
            # Первый ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="sales-trend-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="category-sales-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Второй ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="supplier-performance-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="returns-analysis-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Третий ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="inventory-status-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="top-products-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
        ], fluid=True),
        
        # Скрытые элементы
        dcc.Store(id='business-data-store'),
    ])

def create_business_filters():
    """Создать фильтры для бизнес-аналитики"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_date_filter(), lg=4, md=6),
                dbc.Col([
                    html.Label("Категория товаров", className="form-label"),
                    dcc.Dropdown(
                        id='business-category-filter',
                        options=[{'label': 'Все категории', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=4, md=6, className="mb-3"),
                dbc.Col([
                    html.Label("Поставщик", className="form-label"),
                    dcc.Dropdown(
                        id='supplier-filter',
                        options=[{'label': 'Все поставщики', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=4, md=6, className="mb-3"),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Применить фильтры", id="apply-business-filters", 
                              color="primary", className="me-2"),
                    dbc.Button("Сбросить", id="reset-business-filters", 
                              color="outline-secondary"),
                ], lg=12, className="mb-3"),
            ]),
        ])
    ], className="mb-4")

# Callbacks для бизнес-аналитики
def register_business_callbacks(app):
    """Зарегистрировать callback'ы для бизнес-аналитики"""
    
    @app.callback(
        [Output('business-kpi-cards', 'children'),
         Output('sales-trend-chart', 'figure'),
         Output('category-sales-chart', 'figure'),
         Output('supplier-performance-chart', 'figure'),
         Output('returns-analysis-chart', 'figure'),
         Output('inventory-status-chart', 'figure'),
         Output('top-products-chart', 'figure')],
        [Input('apply-business-filters', 'n_clicks'),
         Input('interval-component', 'n_intervals')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_business_dashboard(n_clicks, n_intervals, start_date, end_date):
        """Обновить дашборд бизнес-аналитики"""
        from datetime import datetime
        
        try:
            # Параметры для запросов
            params = {
                'start_date': start_date,
                'end_date': end_date
            }
            
            # Получение данных
            kpi_data = get_business_kpi_data(params)
            print(123)
            print(kpi_data)
            sales_trend_data = db_manager.execute_query(SALES_TREND_QUERY, params)
            category_data = db_manager.execute_query(CATEGORY_SALES_QUERY, params)
            supplier_data = db_manager.execute_query(SUPPLIER_PERFORMANCE_QUERY, params)
            returns_data = db_manager.execute_query(RETURNS_ANALYSIS_QUERY, params)
            inventory_data = db_manager.execute_query(INVENTORY_STATUS_QUERY, {})
            top_products_data = db_manager.execute_query(TOP_PRODUCTS_QUERY, params)
            
            # Создание KPI карточек
            kpi_cards = create_business_kpi_cards(kpi_data)
            
            # Создание графиков
            sales_fig = chart_builder.create_sales_trend_chart(sales_trend_data)
            category_fig = chart_builder.create_category_sales_chart(category_data)
            supplier_fig = create_supplier_performance_chart(supplier_data)
            returns_fig = chart_builder.create_returns_analysis_chart(returns_data)
            inventory_fig = chart_builder.create_inventory_status_chart(inventory_data)
            top_products_fig = create_top_products_chart(top_products_data)
            
            return [kpi_cards, sales_fig, category_fig, supplier_fig, returns_fig, inventory_fig, top_products_fig]
            
        except Exception as e:
            logger.error(f"Error updating business dashboard: {e}")
            empty_fig = px.line(title="Нет данных")
            return [html.Div("Ошибка загрузки данных")] + [empty_fig] * 6
    
    return app

def get_business_kpi_data(params):
    """Получить данные для KPI бизнес-аналитики"""
    try:
        kpi_result = db_manager.execute_query(KPI_QUERY, params)
        
        if kpi_result.empty:
            return {
                'total_revenue': '0 ₽',
                'total_orders': '0',
                'avg_order_value': '0 ₽',
                'return_rate': '0%'
            }
        
        row = kpi_result.iloc[0]
        total_revenue = row['total_revenue'] or 0
        total_orders = row['total_orders'] or 0
        total_returns = row['total_returns'] or 0
        avg_order_value = row['avg_order_value'] or 0
        
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0
        
        return {
            'total_revenue': data_processor.format_currency(total_revenue),
            'total_orders': f"{total_orders:,}",
            'avg_order_value': data_processor.format_currency(avg_order_value),
            'return_rate': data_processor.format_percentage(return_rate)
        }
        
    except Exception as e:
        logger.error(f"Error getting business KPI data: {e}")
        return {}

def create_business_kpi_cards(kpi_data):
    """Создать KPI карточки для бизнес-аналитики"""
    return dbc.Row([
        dbc.Col(create_kpi_card(
            "💰 Общая выручка", 
            kpi_data.get('total_revenue', '0 ₽')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "📦 Количество заказов", 
            kpi_data.get('total_orders', '0')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "🛒 Средний чек", 
            kpi_data.get('avg_order_value', '0 ₽')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "🔄 Уровень возвратов", 
            kpi_data.get('return_rate', '0%')
        ), lg=3, md=6, className="mb-3"),
    ], className="g-3")

def create_supplier_performance_chart(data):
    """Создать график производительности поставщиков"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.scatter(
        data,
        x='orders_count',
        y='total_revenue',
        size='supplier_rating',
        color='supplier_rating',
        hover_name='supplier_name',
        title='Производительность поставщиков',
        labels={
            'orders_count': 'Количество заказов',
            'total_revenue': 'Общая выручка',
            'supplier_rating': 'Рейтинг поставщика'
        },
        size_max=40
    )
    
    return fig

def create_top_products_chart(data):
    """Создать график топ товаров"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='total_revenue',
        y='product_name',
        orientation='h',
        color='category',
        title='Топ товаров по выручке',
        labels={
            'total_revenue': 'Выручка',
            'product_name': 'Товар',
            'category': 'Категория'
        }
    )
    
    fig.update_layout(showlegend=True)
    return fig