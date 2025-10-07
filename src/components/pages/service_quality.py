from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import logging

from src.database.connection import db_manager
from src.database.queries.service_quality import *
from src.components.kpi_cards import create_kpi_card
from src.components.charts import chart_builder
from src.components.filters import create_date_filter, create_issue_type_filter, create_segment_filter, create_region_filter
from src.utils.data_processor import data_processor

logger = logging.getLogger(__name__)

def create_service_quality_layout():
    """Создать layout для страницы качества обслуживания"""
    return html.Div([
        # Заголовок страницы
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("⭐ Качество обслуживания", 
                           style={'color': '#2C3E50', 'marginBottom': '10px'}),
                    html.P("Анализ поддержки клиентов, возвратов и удовлетворенности", 
                          style={'color': '#7F8C8D', 'marginBottom': '30px'}),
                ])
            ])
        ], fluid=True),
        
        # Фильтры
        create_service_filters(),
        
        # KPI карточки
        html.Div(id="service-kpi-cards", style={'marginBottom': '2rem'}),
        
        # Основные графики
        dbc.Container([
            # Первый ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="support-metrics-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="support-trend-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Второй ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="segment-support-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="resolution-time-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Третий ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="support-returns-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="regional-support-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
        ], fluid=True),
    ])

def create_service_filters():
    """Создать фильтры для качества обслуживания"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_date_filter(), lg=3, md=6),
                dbc.Col(create_region_filter(), lg=3, md=6),
                dbc.Col(create_segment_filter(), lg=3, md=6),
                dbc.Col(create_issue_type_filter(), lg=3, md=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Применить фильтры", id="apply-service-filters", color="primary"),
                    dbc.Button("Сбросить", id="reset-service-filters", color="outline-secondary", className="ms-2")
                ], lg=12, className="mt-2")
            ])
        ])
    ], className="mb-4")

# Callbacks для качества обслуживания
def register_service_callbacks(app):
    @app.callback(
        [Output('service-kpi-cards', 'children'),
         Output('support-metrics-chart', 'figure'),
         Output('support-trend-chart', 'figure'),
         Output('segment-support-chart', 'figure'),
         Output('resolution-time-chart', 'figure'),
         Output('support-returns-chart', 'figure'),
         Output('regional-support-chart', 'figure')],
        [Input('apply-service-filters', 'n_clicks')],
        [State('date-range', 'start_date'),
         State('date-range', 'end_date'),
         State('issue-type-filter', 'value'),
         State('service-segment-filter', 'value'),
         State('service-region-filter', 'value')]
    )
    def update_service_dashboard(n_clicks, start_date, end_date, issue_type, segment, region):
        """Обновить дашборд с применением фильтров"""
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'issue_type': issue_type,
                'segment': segment,
                'region': region
            }

            # SQL-запросы должны учитывать фильтры (см. ниже)
            kpi_data = get_service_kpi_data(params)
            support_data = db_manager.execute_query(SUPPORT_METRICS_QUERY, params)
            support_trend_data = db_manager.execute_query(SUPPORT_TREND_QUERY, params)
            segment_support_data = db_manager.execute_query(SEGMENT_SUPPORT_QUERY, params)
            resolution_time_data = db_manager.execute_query(RESOLUTION_TIME_ANALYSIS_QUERY, params)
            support_returns_data = db_manager.execute_query(SUPPORT_RETURNS_CORRELATION_QUERY, params)
            regional_support_data = db_manager.execute_query(REGIONAL_SUPPORT_QUERY, params)

            # KPI карточки
            kpi_cards = create_service_kpi_cards(kpi_data)

            # Графики
            support_fig = chart_builder.create_support_metrics_chart(support_data)
            support_trend_fig = create_support_trend_chart(support_trend_data)
            segment_support_fig = create_segment_support_chart(segment_support_data)
            resolution_time_fig = create_resolution_time_chart(resolution_time_data)
            support_returns_fig = create_support_returns_chart(support_returns_data)
            regional_support_fig = create_regional_support_chart(regional_support_data)

            return [kpi_cards, support_fig, support_trend_fig, segment_support_fig,
                    resolution_time_fig, support_returns_fig, regional_support_fig]

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            empty_fig = px.bar(title="Нет данных")
            return [html.Div("Ошибка загрузки данных")] + [empty_fig]*6

    # Сброс фильтров
    @app.callback(
        [Output('issue-type-filter', 'value'),
         Output('service-segment-filter', 'value'),
         Output('service-region-filter', 'value'),
         Output('period-selector', 'value')],
        [Input('reset-service-filters', 'n_clicks')]
    )
    def reset_filters(n_clicks):
        return 'all', 'all', 'all', '30d'

    return app

def get_service_kpi_data(params):
    """Получить данные для KPI качества обслуживания"""
    try:
        support_data = db_manager.execute_query(SUPPORT_METRICS_QUERY, params)
        
        if support_data.empty:
            return {
                'total_tickets': '0',
                'avg_resolution_time': '0 мин',
                'resolution_rate': '0%',
                'satisfaction_score': '--'
            }
        
        total_tickets = support_data['tickets_count'].sum()
        avg_resolution_time = support_data['avg_resolution_time'].mean()
        resolution_rate = support_data['resolution_rate'].mean()
        
        return {
            'total_tickets': f"{total_tickets:,}",
            'avg_resolution_time': f"{avg_resolution_time:.0f} мин",
            'resolution_rate': f"{resolution_rate:.1f}%",
            'satisfaction_score': '--'
        }
        
    except Exception as e:
        logger.error(f"Error getting service KPI data: {e}")
        return {}

def create_service_kpi_cards(kpi_data):
    """Создать KPI карточки для качества обслуживания"""
    return dbc.Row([
        dbc.Col(create_kpi_card(
            "📞 Всего обращений", 
            kpi_data.get('total_tickets', '0')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "⏱️ Ср. время решения", 
            kpi_data.get('avg_resolution_time', '0 мин')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "✅ Уровень решения", 
            kpi_data.get('resolution_rate', '0%')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "⭐ Удовлетворенность", 
            kpi_data.get('satisfaction_score', '--')
        ), lg=3, md=6, className="mb-3"),
    ], className="g-3")

def create_support_trend_chart(data):
    """Создать график тренда обращений"""
    if data.empty:
        return px.line(title="Нет данных")
    
    fig = px.line(
        data,
        x='date',
        y='daily_tickets',
        title='Динамика обращений в поддержку',
        labels={'daily_tickets': 'Количество обращений', 'date': 'Дата'}
    )
    
    return fig

def create_segment_support_chart(data):
    """Создать график поддержки по сегментам"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='segment',
        y='tickets_count',
        title='Обращения по сегментам клиентов',
        labels={'tickets_count': 'Количество обращений', 'segment': 'Сегмент'},
        color='resolution_rate'
    )
    
    return fig

def create_resolution_time_chart(data):
    """Создать график времени решения"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='resolution_time_bucket',
        y='tickets_count',
        title='Распределение времени решения обращений',
        labels={'tickets_count': 'Количество обращений', 'resolution_time_bucket': 'Время решения'}
    )
    
    return fig

def create_support_returns_chart(data):
    """Создать график связи поддержки и возвратов"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='issue_type',
        y=['support_tickets', 'returns_count'],
        title='Связь обращений и возвратов',
        labels={'value': 'Количество', 'variable': 'Метрика'},
        barmode='group'
    )
    
    return fig

def create_regional_support_chart(data):
    """Создать график поддержки по регионам"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='region',
        y='tickets_count',
        title='Обращения по регионам',
        labels={'tickets_count': 'Количество обращений', 'region': 'Регион'},
        color='avg_resolution_time'
    )
    
    return fig