from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import logging

from src.database.connection import db_manager
from src.database.queries.customer_behavior import *
from src.components.kpi_cards import create_kpi_card
from src.components.charts import chart_builder
from src.components.filters import create_date_filter
from src.utils.data_processor import data_processor

logger = logging.getLogger(__name__)

def create_customer_behavior_layout():
    """Создать layout для страницы клиентов и поведения"""
    return html.Div([
        # Заголовок страницы
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("👥 Клиенты и поведение", 
                           style={'color': '#2C3E50', 'marginBottom': '10px'}),
                    html.P("Анализ сегментации, воронки продаж и лояльности клиентов", 
                          style={'color': '#7F8C8D', 'marginBottom': '30px'}),
                ])
            ])
        ], fluid=True),
        
        # Фильтры
        create_customer_filters(),
        
        # KPI карточки
        html.Div(id="customer-kpi-cards", style={'marginBottom': '2rem'}),
        
        # Основные графики
        dbc.Container([
            # Первый ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="user-segments-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="funnel-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Второй ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="regional-activity-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="segment-behavior-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Третий ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="traffic-channels-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="user-devices-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Четвертый ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="customer-loyalty-chart"),
                    lg=12, className="mb-4"
                ),
            ]),
        ], fluid=True),
    ])

def create_customer_filters():
    """Создать фильтры для анализа клиентов"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_date_filter(), lg=3, md=6),
                dbc.Col([
                    html.Label("Сегмент клиентов", className="form-label"),
                    dcc.Dropdown(
                        id='customer-segment-filter',
                        options=[{'label': 'Все сегменты', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=3, md=6, className="mb-3"),
                dbc.Col([
                    html.Label("Регион", className="form-label"),
                    dcc.Dropdown(
                        id='region-filter',
                        options=[{'label': 'Все регионы', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=3, md=6, className="mb-3"),
                dbc.Col([
                    html.Label("Канал трафика", className="form-label"),
                    dcc.Dropdown(
                        id='traffic-channel-filter',
                        options=[{'label': 'Все каналы', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=3, md=6, className="mb-3"),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Применить фильтры", id="apply-customer-filters", 
                              color="primary", className="me-2"),
                    dbc.Button("Сбросить", id="reset-customer-filters", 
                              color="outline-secondary"),
                ], lg=12, className="mb-3"),
            ]),
        ])
    ], className="mb-4")

# Callbacks для клиентов и поведения
def register_customer_callbacks(app):
    """Зарегистрировать callback'ы для анализа клиентов"""
    
    @app.callback(
        [Output('customer-kpi-cards', 'children'),
         Output('user-segments-chart', 'figure'),
         Output('funnel-chart', 'figure'),
         Output('regional-activity-chart', 'figure'),
         Output('segment-behavior-chart', 'figure'),
         Output('traffic-channels-chart', 'figure'),
         Output('user-devices-chart', 'figure'),
         Output('customer-loyalty-chart', 'figure')],
        [Input('apply-customer-filters', 'n_clicks'),
         Input('interval-component', 'n_intervals')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_customer_dashboard(n_clicks, n_intervals, start_date, end_date):
        """Обновить дашборд клиентов и поведения"""
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date
            }
            
            # Получение данных
            kpi_data = get_customer_kpi_data(params)
            segments_data = db_manager.execute_query(USER_SEGMENTS_QUERY, {})
            funnel_data = db_manager.execute_query(EVENTS_FUNNEL_QUERY, params)
            regional_data = db_manager.execute_query(REGIONAL_ACTIVITY_QUERY, params)
            segment_behavior_data = db_manager.execute_query(SEGMENT_BEHAVIOR_QUERY, params)
            traffic_data = db_manager.execute_query(TRAFFIC_CHANNELS_QUERY, params)
            devices_data = db_manager.execute_query(USER_DEVICES_QUERY, params)
            loyalty_data = db_manager.execute_query(CUSTOMER_LOYALTY_QUERY, params)
            
            # Создание KPI карточек
            kpi_cards = create_customer_kpi_cards(kpi_data)
            
            # Создание графиков
            segments_fig = chart_builder.create_segmentation_chart(segments_data)
            funnel_fig = chart_builder.create_funnel_chart(funnel_data)
            regional_fig = create_regional_activity_chart(regional_data)
            segment_behavior_fig = create_segment_behavior_chart(segment_behavior_data)
            traffic_fig = chart_builder.create_traffic_channels_chart(traffic_data)
            devices_fig = create_user_devices_chart(devices_data)
            loyalty_fig = create_customer_loyalty_chart(loyalty_data)
            
            return [kpi_cards, segments_fig, funnel_fig, regional_fig, 
                   segment_behavior_fig, traffic_fig, devices_fig, loyalty_fig]
            
        except Exception as e:
            logger.error(f"Error updating customer dashboard: {e}")
            empty_fig = px.pie(title="Нет данных")
            return [html.Div("Ошибка загрузки данных")] + [empty_fig] * 7
    
    return app

def get_customer_kpi_data(params):
    """Получить данные для KPI клиентов"""
    try:
        # Расчет основных метрик клиентов
        segments_data = db_manager.execute_query(USER_SEGMENTS_QUERY, {})
        funnel_data = db_manager.execute_query(EVENTS_FUNNEL_QUERY, params)
        
        total_users = segments_data['users_count'].sum() if not segments_data.empty else 0
        
        # Расчет конверсии из воронки
        conversion_rate = 0
        if not funnel_data.empty:
            views = funnel_data[funnel_data['event_type'] == 'view']['events_count'].sum()
            purchases = funnel_data[funnel_data['event_type'] == 'purchase']['events_count'].sum()
            conversion_rate = (purchases / views * 100) if views > 0 else 0
        
        return {
            'total_users': f"{total_users:,}",
            'conversion_rate': f"{conversion_rate:.1f}%",
            'avg_session_duration': '--',
            'bounce_rate': '--'
        }
        
    except Exception as e:
        logger.error(f"Error getting customer KPI data: {e}")
        return {}

def create_customer_kpi_cards(kpi_data):
    """Создать KPI карточки для клиентов"""
    return dbc.Row([
        dbc.Col(create_kpi_card(
            "👥 Всего пользователей", 
            kpi_data.get('total_users', '0')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "📊 Конверсия", 
            kpi_data.get('conversion_rate', '0%')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "⏱️ Ср. время сессии", 
            kpi_data.get('avg_session_duration', '--')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "🎯 Отскок", 
            kpi_data.get('bounce_rate', '--')
        ), lg=3, md=6, className="mb-3"),
    ], className="g-3")

def create_regional_activity_chart(data):
    """Создать график активности по регионам"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='region',
        y='total_orders',
        title='Активность по регионам',
        labels={'total_orders': 'Количество заказов', 'region': 'Регион'},
        color='total_orders'
    )
    
    return fig

def create_segment_behavior_chart(data):
    """Создать график поведения сегментов"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='segment',
        y='total_orders',
        title='Поведение сегментов клиентов',
        labels={'total_orders': 'Количество заказов', 'segment': 'Сегмент'},
        color='avg_order_value'
    )
    
    return fig

def create_user_devices_chart(data):
    """Создать график устройств пользователей"""
    if data.empty:
        return px.pie(title="Нет данных")
    
    fig = px.pie(
        data,
        values='sessions_count',
        names='device',
        title='Распределение по устройствам'
    )
    
    return fig

def create_customer_loyalty_chart(data):
    """Создать график лояльности клиентов"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='loyalty_level',
        y='customers_count',
        title='Уровни лояльности клиентов',
        labels={'customers_count': 'Количество клиентов', 'loyalty_level': 'Уровень лояльности'},
        color='avg_order_value'
    )
    
    return fig