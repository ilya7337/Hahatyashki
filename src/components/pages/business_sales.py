from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go 
import pandas as pd
import logging

from src.database.connection import db_manager
from src.database.queries.business_sales import *
from src.components.kpi_cards import create_kpi_card
from src.components.charts import chart_builder
from src.components.filters import create_date_filter, create_category_filter, create_supplier_filter
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
                           className="business-sales-title"),
                    html.P("Анализ продаж, выручки, поставщиков и складских запасов", 
                          className="business-sales-subtitle"),
                ])
            ])
        ], fluid=True, className="business-sales-container"),
        
        # Фильтры
        create_business_filters(),
        
        # KPI карточки
        html.Div(id="business-kpi-cards", className="business-kpi-section"),
        
        # Основные графики
        dbc.Container([
            # Первый ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="sales-trend-chart"),
                    lg=6, className="business-chart-container"
                ),
                dbc.Col(
                    dcc.Graph(id="category-sales-chart"),
                    lg=6, className="business-chart-container"
                ),
            ]),
            
            # Второй ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="supplier-performance-chart"),
                    lg=6, className="business-chart-container"
                ),
                dbc.Col(
                    dcc.Graph(id="returns-analysis-chart"),
                    lg=6, className="business-chart-container"
                ),
            ]),
            
            # Третий ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="inventory-status-chart"),
                    lg=6, className="business-chart-container"
                ),
                dbc.Col(
                    dcc.Graph(id="top-products-chart"),
                    lg=6, className="business-chart-container"
                ),
            ]),
        ], fluid=True),
        
        # Скрытые элементы
        dcc.Store(id='business-data-store'),
    ], className="business-sales-container")

def create_business_filters():
    """Создать фильтры для бизнес-аналитики"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_date_filter(), lg=4, md=6),
                dbc.Col(create_category_filter(), lg=4, md=6),
                dbc.Col(create_supplier_filter(), lg=4, md=6),
            ]),
        ])
    ], className="business-filters-card")

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
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('basic-category-filter', 'value'),
         Input('supplier-filter', 'value')]
    )
    def update_business_dashboard(start_date, end_date, selected_category, supplier):
        """Обновить дашборд бизнес-аналитики"""
        from datetime import datetime
        try:
            print(supplier)
            # Параметры для запросов
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'category': selected_category if selected_category != 'all' else None,
                'supplier': supplier if supplier != 'all' else None,
            }
            
            # Получение данных
            kpi_data = get_business_kpi_data(params)
            sales_trend_data = db_manager.execute_query(SALES_TREND_QUERY, params)
            category_data = db_manager.execute_query(CATEGORY_SALES_QUERY, params)
            supplier_data = db_manager.execute_query(SUPPLIER_PERFORMANCE_QUERY, params)
            returns_data = db_manager.execute_query(RETURNS_ANALYSIS_QUERY, params)
            inventory_data = db_manager.execute_query(INVENTORY_STATUS_QUERY, params)
            top_products_data = db_manager.execute_query(TOP_PRODUCTS_QUERY, params)
            
            # Создание KPI карточек
            kpi_cards = create_business_kpi_cards(kpi_data)
            
            # Создание графиков с улучшенным дизайном
            sales_fig = create_enhanced_sales_trend_chart(sales_trend_data)
            category_fig = create_enhanced_category_sales_chart(category_data)
            supplier_fig = create_enhanced_supplier_performance_chart(supplier_data)
            returns_fig = create_enhanced_returns_analysis_chart(returns_data)
            inventory_fig = create_enhanced_inventory_status_chart(inventory_data)
            top_products_fig = create_enhanced_top_products_chart(top_products_data)
            
            return [kpi_cards, sales_fig, category_fig, supplier_fig, returns_fig, inventory_fig, top_products_fig]
            
        except Exception as e:
            logger.error(f"Error updating business dashboard: {e}")
            empty_fig = create_empty_chart()
            return [html.Div("Ошибка загрузки данных", className="text-danger")] + [empty_fig] * 6
    
    return app

def create_empty_chart():
    """Создать пустой график с единым стилем"""
    fig = go.Figure()
    fig.update_layout(
        title=dict(
            text="Нет данных",
            x=0.5,
            font=dict(size=16, color="#6c757d")
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

def create_enhanced_sales_trend_chart(data):
    """Создать улучшенный график динамики продаж"""
    if data.empty:
        return create_empty_chart()
    
    fig = px.line(
        data,
        x='date',
        y='daily_revenue',
        title='Динамика продаж',
        color_discrete_sequence=['#2E86AB']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2C3E50"),
        title_font_size=18,
        height=400
    )
    
    return fig

def create_enhanced_category_sales_chart(data):
    """Создать улучшенный график продаж по категориям"""
    if data.empty:
        return create_empty_chart()
    
    fig = px.bar(
        data,
        x='category_revenue',
        y='category',
        orientation='h',
        title='Продажи по категориям',
        color='category_revenue',
        color_continuous_scale=['#A23B72', '#F18F01', '#C73E1D']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2C3E50"),
        title_font_size=18,
        height=400,
        showlegend=False
    )
    
    return fig

def create_enhanced_supplier_performance_chart(data):
    """Создать улучшенный график производительности поставщиков"""
    if data.empty:
        return create_empty_chart()
    
    fig = go.Figure()
    
    # Добавляем столбцы для выручки
    fig.add_trace(go.Bar(
        name='Выручка',
        x=data['supplier_name'],
        y=data['total_revenue'],
        marker_color='#2E86AB',
        hovertemplate='<b>%{x}</b><br>Выручка: %{y:,.0f} руб<br>Заказы: %{customdata}',
        customdata=data['orders_count']
    ))
    
    # Добавляем линию для рейтинга
    fig.add_trace(go.Scatter(
        name='Рейтинг',
        x=data['supplier_name'],
        y=data['supplier_rating'],
        mode='lines+markers',
        line=dict(color='#F18F01', width=3),
        marker=dict(size=8, color='#F18F01'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Рейтинг: %{y:.1f}'
    ))
    
    fig.update_layout(
        title='Производительность поставщиков',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2C3E50"),
        xaxis=dict(tickangle=45),
        yaxis=dict(title='Выручка (руб)', titlefont=dict(color='#2E86AB')),
        yaxis2=dict(
            title='Рейтинг',
            titlefont=dict(color='#F18F01'),
            overlaying='y',
            side='right',
            range=[0, 5]
        ),
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_enhanced_returns_analysis_chart(data):
    """Создать улучшенный график анализа возвратов"""
    if data.empty:
        return create_empty_chart()
    
    fig = px.pie(
        data,
        values='returns_count',
        names='reason',
        title='Анализ возвратов по причинам',
        color_discrete_sequence=['#A23B72', '#F18F01', '#C73E1D', '#3C91E6', '#2E86AB']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2C3E50"),
        title_font_size=18,
        height=400
    )
    
    return fig

def create_enhanced_inventory_status_chart(data):
    """Создать улучшенный график статуса склада"""
    if data.empty:
        return create_empty_chart()
    
    fig = px.bar(
        data,
        x='total_stock',
        y='category',
        orientation='h',
        title='Остатки на складе по категориям',
        color='total_stock',
        color_continuous_scale=['#3C91E6', '#2E86AB']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2C3E50"),
        title_font_size=18,
        height=400,
        showlegend=False
    )
    
    return fig

def create_enhanced_top_products_chart(data):
    """Создать улучшенный график топ товаров"""
    if data.empty:
        return create_empty_chart()
    
    fig = px.bar(
        data,
        x='total_revenue',
        y='product_name',
        orientation='h',
        title='Топ товаров по выручке',
        color='total_revenue',
        color_continuous_scale=['#C73E1D', '#F18F01']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#2C3E50"),
        title_font_size=18,
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

# Остальные функции остаются без изменений
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
        ), lg=3, md=6, className="mb-3 kpi-card-revenue"),
        
        dbc.Col(create_kpi_card(
            "📦 Количество заказов", 
            kpi_data.get('total_orders', '0')
        ), lg=3, md=6, className="mb-3 kpi-card-orders"),
        
        dbc.Col(create_kpi_card(
            "🛒 Средний чек", 
            kpi_data.get('avg_order_value', '0 ₽')
        ), lg=3, md=6, className="mb-3 kpi-card-avg-order"),
        
        dbc.Col(create_kpi_card(
            "🔄 Уровень возвратов", 
            kpi_data.get('return_rate', '0%')
        ), lg=3, md=6, className="mb-3 kpi-card-returns"),
    ], className="g-3")