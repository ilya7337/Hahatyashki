from dash import html, dcc, Input, Output, callback, State
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
                    html.Label("📊 Кампания", className="form-label"),
                    dcc.Dropdown(
                        id='campaign-filter',
                        options=[],  # Будет заполнено через callback
                        value='all',
                        clearable=False,
                        placeholder="Загрузка кампаний..."
                    ),
                ], lg=4, md=6, className="mb-3"),
                dbc.Col([
                    html.Label("🌐 Канал трафика", className="form-label"),
                    dcc.Dropdown(
                        id='ad-channel-filter',
                        options=[],  # Будет заполнено через callback
                        value='all',
                        clearable=False,
                        placeholder="Загрузка каналов..."
                    ),
                ], lg=4, md=6, className="mb-3"),
                dbc.Col([
                    html.Label("📦 Категория товаров", className="form-label"),
                    dcc.Dropdown(
                        id='ad-category-filter',
                        options=[],  # Будет заполнено через callback
                        value='all',
                        clearable=False,
                        placeholder="Загрузка категорий..."
                    ),
                ], lg=4, md=6, className="mb-3"),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Применить фильтры", id="apply-service-filters", color="primary"),
                    dbc.Button("Сбросить", id="reset-service-filters", color="outline-secondary", className="ms-2")
                ], lg=12, className="mt-2")
            ])
        ])
    ], className="mb-4")


def register_advertising_callbacks(app):
    # Callbacks для загрузки фильтров из базы данных
    @app.callback(
        Output('campaign-filter', 'options'),
        [Input('interval-component', 'n_intervals')]
    )
    def load_campaigns(n_intervals):
        """Загрузить кампании из базы данных"""
        try:
            logger.info("Loading campaigns from database...")
            query = "SELECT DISTINCT campaign_name FROM ad_revenue WHERE campaign_name IS NOT NULL AND campaign_name != '' ORDER BY campaign_name"
            return load_filter_options(query, "Все кампании")
        except Exception as e:
            logger.error(f"Error loading campaigns: {e}")
            return [{'label': 'Все кампании', 'value': 'all'}]

    @app.callback(
        Output('ad-channel-filter', 'options'),
        [Input('interval-component', 'n_intervals')]
    )
    def load_ad_channels(n_intervals):
        """Загрузить каналы трафика для рекламы"""
        try:
            logger.info("Loading ad channels from database...")
            query = "SELECT DISTINCT channel FROM traffic WHERE channel IS NOT NULL AND channel != '' ORDER BY channel"
            return load_filter_options(query, "Все каналы")
        except Exception as e:
            logger.error(f"Error loading ad channels: {e}")
            return [{'label': 'Все каналы', 'value': 'all'}]

    @app.callback(
        Output('ad-category-filter', 'options'),
        [Input('interval-component', 'n_intervals')]
    )
    def load_ad_categories(n_intervals):
        """Загрузить категории для рекламы"""
        try:
            logger.info("Loading categories for advertising from database...")
            query = "SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != '' ORDER BY category"
            return load_filter_options(query, "Все категории")
        except Exception as e:
            logger.error(f"Error loading categories for advertising: {e}")
            return [{'label': 'Все категории', 'value': 'all'}]

    def load_filter_options(query, default_label="Все"):
        """Вспомогательная функция для загрузки опций фильтра"""
        try:
            result = db_manager.execute_query(query)
            if not result.empty:
                column_name = result.columns[0]
                options = [{'label': default_label, 'value': 'all'}]
                for _, row in result.iterrows():
                    value = row[column_name]
                    if value:
                        options.append({
                            'label': str(value),
                            'value': str(value)
                        })
                logger.info(f"Успешно загружено {len(options)} опций для фильтра")
                return options
            else:
                logger.warning(f"Нет данных для запроса: {query}")
                return [{'label': default_label, 'value': 'all'}]
                
        except Exception as e:
            logger.error(f"Ошибка загрузки опций фильтра: {e}")
            return [{'label': default_label, 'value': 'all'}]

    # Основной callback для обновления дашборда
    @app.callback(
        [Output('advertising-kpi-cards', 'children'),
        Output('ad-performance-chart', 'figure'),
        Output('ad-trend-chart', 'figure'),
        Output('product-ad-performance-chart', 'figure'),
        Output('channel-conversion-chart', 'figure'),
        Output('roi-trend-chart', 'figure'),
        Output('top-ctr-campaigns-chart', 'figure')],
        [Input('apply-service-filters', 'n_clicks')],
        [State('date-range', 'start_date'),
        State('date-range', 'end_date'),
        State('campaign-filter', 'value'),
        State('ad-channel-filter', 'value'),
        State('ad-category-filter', 'value')]
    )
    def update_advertising_dashboard(n_clicks, start_date, end_date, selected_campaign, selected_channel, selected_category):
        """Обновить дашборд рекламы и маркетинга"""
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'campaign': selected_campaign if selected_campaign != 'all' else None,
                'channel': selected_channel if selected_channel != 'all' else None,
                'category': selected_category if selected_category != 'all' else None
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