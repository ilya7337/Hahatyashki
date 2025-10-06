from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import logging

from src.database.connection import db_manager
from src.database.queries.advertising_marketing import *
from src.components.kpi_cards import create_kpi_card
from src.components.charts import chart_builder
from src.components.filters import create_date_filter
from src.utils.data_processor import data_processor

logger = logging.getLogger(__name__)

def create_advertising_marketing_layout():
    """Создать layout для страницы рекламы и маркетинга"""
    return html.Div([
        # Заголовок страницы
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📢 Реклама и маркетинг", 
                           style={'color': '#2C3E50', 'marginBottom': '10px'}),
                    html.P("Анализ ROI кампаний, конверсии и эффективности рекламы", 
                          style={'color': '#7F8C8D', 'marginBottom': '30px'}),
                ])
            ])
        ], fluid=True),
        
        # Фильтры
        create_advertising_filters(),
        
        # KPI карточки
        html.Div(id="advertising-kpi-cards", style={'marginBottom': '2rem'}),
        
        # Основные графики
        dbc.Container([
            # Первый ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="ad-performance-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="ad-trend-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Второй ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="product-ad-performance-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="channel-conversion-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
            
            # Третий ряд
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id="roi-trend-chart"),
                    lg=6, className="mb-4"
                ),
                dbc.Col(
                    dcc.Graph(id="top-ctr-campaigns-chart"),
                    lg=6, className="mb-4"
                ),
            ]),
        ], fluid=True),
    ])

def create_advertising_filters():
    """Создать фильтры для рекламы и маркетинга"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_date_filter(), lg=4, md=6),
                dbc.Col([
                    html.Label("Кампания", className="form-label"),
                    dcc.Dropdown(
                        id='campaign-filter',
                        options=[{'label': 'Все кампании', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=4, md=6, className="mb-3"),
                dbc.Col([
                    html.Label("Канал трафика", className="form-label"),
                    dcc.Dropdown(
                        id='ad-channel-filter',
                        options=[{'label': 'Все каналы', 'value': 'all'}],
                        value='all',
                        clearable=False,
                    ),
                ], lg=4, md=6, className="mb-3"),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Применить фильтры", id="apply-advertising-filters", 
                              color="primary", className="me-2"),
                    dbc.Button("Сбросить", id="reset-advertising-filters", 
                              color="outline-secondary"),
                ], lg=12, className="mb-3"),
            ]),
        ])
    ], className="mb-4")

# Callbacks для рекламы и маркетинга
def register_advertising_callbacks(app):
    """Зарегистрировать callback'ы для рекламы"""
    
    @app.callback(
        [Output('advertising-kpi-cards', 'children'),
         Output('ad-performance-chart', 'figure'),
         Output('ad-trend-chart', 'figure'),
         Output('product-ad-performance-chart', 'figure'),
         Output('channel-conversion-chart', 'figure'),
         Output('roi-trend-chart', 'figure'),
         Output('top-ctr-campaigns-chart', 'figure')],
        [Input('apply-advertising-filters', 'n_clicks'),
         Input('interval-component', 'n_intervals')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_advertising_dashboard(n_clicks, n_intervals, start_date, end_date):
        """Обновить дашборд рекламы и маркетинга"""
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date
            }
            
            # Получение данных
            kpi_data = get_advertising_kpi_data(params)
            ad_performance_data = db_manager.execute_query(AD_PERFORMANCE_QUERY, params)
            ad_trend_data = db_manager.execute_query(AD_TREND_QUERY, params)
            product_ad_data = db_manager.execute_query(PRODUCT_AD_PERFORMANCE_QUERY, params)
            channel_data = db_manager.execute_query(CHANNEL_CONVERSION_QUERY, params)
            roi_trend_data = db_manager.execute_query(ROI_TREND_QUERY, params)
            ctr_data = db_manager.execute_query(TOP_CTR_CAMPAIGNS_QUERY, params)
            
            # Создание KPI карточек
            kpi_cards = create_advertising_kpi_cards(kpi_data)
            
            # Создание графиков
            ad_performance_fig = create_ad_performance_chart(ad_performance_data)
            ad_trend_fig = create_ad_trend_chart(ad_trend_data)
            product_ad_fig = create_product_ad_performance_chart(product_ad_data)
            channel_fig = create_channel_conversion_chart(channel_data)
            roi_trend_fig = create_roi_trend_chart(roi_trend_data)
            ctr_fig = create_top_ctr_campaigns_chart(ctr_data)
            
            return [kpi_cards, ad_performance_fig, ad_trend_fig, product_ad_fig, 
                   channel_fig, roi_trend_fig, ctr_fig]
            
        except Exception as e:
            logger.error(f"Error updating advertising dashboard: {e}")
            empty_fig = px.bar(title="Нет данных")
            return [html.Div("Ошибка загрузки данных")] + [empty_fig] * 6
    
    return app

def get_advertising_kpi_data(params):
    """Получить данные для KPI рекламы"""
    try:
        ad_performance_data = db_manager.execute_query(AD_PERFORMANCE_QUERY, params)
        
        if ad_performance_data.empty:
            return {
                'total_revenue': '0 ₽',
                'total_spend': '0 ₽',
                'avg_roi': '0%',
                'avg_ctr': '0%'
            }
        
        total_revenue = ad_performance_data['total_revenue'].sum()
        total_spend = ad_performance_data['total_spend'].sum()
        avg_roi = ad_performance_data['roi'].mean() * 100
        avg_ctr = ad_performance_data['ctr'].mean()
        
        return {
            'total_revenue': data_processor.format_currency(total_revenue),
            'total_spend': data_processor.format_currency(total_spend),
            'avg_roi': f"{avg_roi:.1f}%",
            'avg_ctr': f"{avg_ctr:.1f}%"
        }
        
    except Exception as e:
        logger.error(f"Error getting advertising KPI data: {e}")
        return {}

def create_advertising_kpi_cards(kpi_data):
    """Создать KPI карточки для рекламы"""
    return dbc.Row([
        dbc.Col(create_kpi_card(
            "💰 Доход от рекламы", 
            kpi_data.get('total_revenue', '0 ₽')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "💸 Расходы на рекламу", 
            kpi_data.get('total_spend', '0 ₽')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "📈 Средний ROI", 
            kpi_data.get('avg_roi', '0%')
        ), lg=3, md=6, className="mb-3"),
        
        dbc.Col(create_kpi_card(
            "🎯 Средний CTR", 
            kpi_data.get('avg_ctr', '0%')
        ), lg=3, md=6, className="mb-3"),
    ], className="g-3")

def create_ad_performance_chart(data):
    """Создать график эффективности рекламы"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='campaign_name',
        y='roi',
        title='ROI рекламных кампаний',
        labels={'roi': 'ROI', 'campaign_name': 'Кампания'},
        color='roi'
    )
    
    return fig

def create_ad_trend_chart(data):
    """Создать график трендов рекламы"""
    if data.empty:
        return px.line(title="Нет данных")
    
    fig = px.line(
        data,
        x='date',
        y=['daily_revenue', 'daily_spend'],
        title='Динамика доходов и расходов на рекламу',
        labels={'value': 'Сумма', 'variable': 'Метрика'}
    )
    
    return fig

def create_product_ad_performance_chart(data):
    """Создать график эффективности рекламы по товарам"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='product_name',
        y='roi',
        title='ROI по товарам',
        labels={'roi': 'ROI', 'product_name': 'Товар'},
        color='category'
    )
    
    return fig

def create_channel_conversion_chart(data):
    """Создать график конверсии по каналам"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='channel',
        y='conversion_rate',
        title='Конверсия по каналам трафика',
        labels={'conversion_rate': 'Конверсия (%)', 'channel': 'Канал'},
        color='conversion_rate'
    )
    
    return fig

def create_roi_trend_chart(data):
    """Создать график тренда ROI"""
    if data.empty:
        return px.line(title="Нет данных")
    
    fig = px.line(
        data,
        x='week_start',
        y='weekly_roi',
        title='Тренд ROI по неделям',
        labels={'weekly_roi': 'ROI', 'week_start': 'Неделя'}
    )
    
    return fig

def create_top_ctr_campaigns_chart(data):
    """Создать график топ кампаний по CTR"""
    if data.empty:
        return px.bar(title="Нет данных")
    
    fig = px.bar(
        data,
        x='campaign_name',
        y='ctr',
        title='Топ кампаний по CTR',
        labels={'ctr': 'CTR (%)', 'campaign_name': 'Кампания'},
        color='ctr'
    )
    
    return fig