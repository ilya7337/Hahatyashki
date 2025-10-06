from dash import Input, Output, State, callback_context, no_update
from datetime import datetime, timedelta
import pandas as pd
import logging

from src.database.connection import db_manager
from src.database.queries import *
from src.components.kpi_cards import create_kpi_cards
from src.components.charts import chart_builder
from src.utils.data_processor import data_processor
from src.utils.calculations import MetricCalculator

logger = logging.getLogger(__name__)

def register_callbacks(app):
    """Зарегистрировать все callback'и приложения"""
    
    @app.callback(
        [Output('kpi-cards-container', 'children'),
         Output('sales-trend', 'figure'),
         Output('category-sales', 'figure'),
         Output('funnel-chart', 'figure'),
         Output('segmentation-chart', 'figure'),
         Output('ad-performance', 'figure'),
         Output('returns-analysis', 'figure'),
         Output('traffic-channels', 'figure'),
         Output('inventory-status', 'figure'),
         Output('support-metrics', 'figure'),
         Output('supplier-performance', 'figure')],
        [Input('apply-filters', 'n_clicks'),
         Input('interval-component', 'n_intervals')],
        [State('date-range', 'start_date'),
         State('date-range', 'end_date'),
         State('category-filter', 'value'),
         State('segment-filter', 'value'),
         State('channel-filter', 'value')]
    )
    def update_dashboard(n_clicks, n_intervals, start_date, end_date, category, segment, channel):
        """Основной callback для обновления всего дашборда"""
        
        # Преобразуем даты в правильный формат
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            # Используем даты по умолчанию
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        
        # Параметры для запросов
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        try:
            logger.info(f"Updating dashboard with params: {params}")
            
            # Получение данных из БД
            kpi_data = get_kpi_data(params)
            sales_trend_data = db_manager.execute_query(SALES_TREND_QUERY, params)
            category_sales_data = db_manager.execute_query(CATEGORY_SALES_QUERY, params)
            funnel_data = db_manager.execute_query(EVENTS_FUNNEL_QUERY, params)
            segmentation_data = db_manager.execute_query(USER_SEGMENTS_QUERY, {})
            ad_performance_data = db_manager.execute_query(AD_PERFORMANCE_QUERY, params)
            returns_data = db_manager.execute_query(RETURNS_ANALYSIS_QUERY, params)
            traffic_data = db_manager.execute_query(TRAFFIC_CHANNELS_QUERY, params)
            inventory_data = db_manager.execute_query(INVENTORY_STATUS_QUERY, {})
            support_data = db_manager.execute_query(SUPPORT_METRICS_QUERY, params)
            supplier_data = db_manager.execute_query(SUPPLIER_PERFORMANCE_QUERY, params)
            
            # Логируем размеры полученных данных
            logger.info(f"Sales trend data: {len(sales_trend_data)} rows")
            logger.info(f"Category sales data: {len(category_sales_data)} rows")
            logger.info(f"Funnel data: {len(funnel_data)} rows")
            
            # Создание KPI карточек
            kpi_cards = create_kpi_cards(kpi_data)
            
            # Создание графиков
            sales_trend_fig = chart_builder.create_sales_trend_chart(sales_trend_data)
            category_sales_fig = chart_builder.create_category_sales_chart(category_sales_data)
            funnel_fig = chart_builder.create_funnel_chart(funnel_data)
            segmentation_fig = chart_builder.create_segmentation_chart(segmentation_data)
            ad_performance_fig = chart_builder.create_ad_performance_chart(ad_performance_data)
            returns_fig = chart_builder.create_returns_analysis_chart(returns_data)
            traffic_fig = chart_builder.create_traffic_channels_chart(traffic_data)
            inventory_fig = chart_builder.create_inventory_status_chart(inventory_data)
            support_fig = chart_builder.create_support_metrics_chart(support_data)
            supplier_fig = chart_builder.create_supplier_performance_chart(supplier_data)
            
            logger.info("Dashboard updated successfully")
            
            return [
                kpi_cards,
                sales_trend_fig,
                category_sales_fig,
                funnel_fig,
                segmentation_fig,
                ad_performance_fig,
                returns_fig,
                traffic_fig,
                inventory_fig,
                support_fig,
                supplier_fig
            ]
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            # Возвращаем пустые графики в случае ошибки
            empty_fig = chart_builder.create_sales_trend_chart(pd.DataFrame())
            return [create_kpi_cards({})] + [empty_fig] * 10
    
    @app.callback(
        [Output('category-filter', 'options'),
         Output('segment-filter', 'options'),
         Output('channel-filter', 'options')],
        [Input('apply-filters', 'n_clicks')]
    )
    def update_filter_options(n_clicks):
        """Обновить опции фильтров"""
        try:
            # Получаем уникальные значения для фильтров
            categories = db_manager.execute_query(
                "SELECT DISTINCT category FROM products ORDER BY category", {}
            )
            segments = db_manager.execute_query(
                "SELECT DISTINCT segment FROM user_segments ORDER BY segment", {}
            )
            channels = db_manager.execute_query(
                "SELECT DISTINCT channel FROM traffic ORDER BY channel", {}
            )
            
            category_options = [{'label': 'Все категории', 'value': 'all'}] + [
                {'label': row['category'], 'value': row['category']} 
                for _, row in categories.iterrows()
            ]
            
            segment_options = [{'label': 'Все сегменты', 'value': 'all'}] + [
                {'label': row['segment'], 'value': row['segment']} 
                for _, row in segments.iterrows()
            ]
            
            channel_options = [{'label': 'Все каналы', 'value': 'all'}] + [
                {'label': row['channel'], 'value': row['channel']} 
                for _, row in channels.iterrows()
            ]
            
            return category_options, segment_options, channel_options
            
        except Exception as e:
            logger.error(f"Error updating filter options: {e}")
            return [{'label': 'Все категории', 'value': 'all'}], [{'label': 'Все сегменты', 'value': 'all'}], [{'label': 'Все каналы', 'value': 'all'}]
    
    @app.callback(
        [Output('date-range', 'start_date'),
         Output('date-range', 'end_date'),
         Output('category-filter', 'value'),
         Output('segment-filter', 'value'),
         Output('channel-filter', 'value')],
        [Input('reset-filters', 'n_clicks')]
    )
    def reset_filters(n_clicks):
        """Сбросить фильтры к значениям по умолчанию"""
        if n_clicks:
            end_date = datetime.now().date()
            start_date = (end_date - timedelta(days=30))
            
            return start_date, end_date, 'all', 'all', 'all'
        
        return no_update

def get_kpi_data(params: dict) -> dict:
    """Получить данные для KPI карточек"""
    try:
        # Основные KPI
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
        
        # Форматирование значений
        formatted_data = {
            'total_revenue': data_processor.format_currency(total_revenue),
            'total_orders': f"{total_orders:,}",
            'avg_order_value': data_processor.format_currency(avg_order_value),
            'return_rate': data_processor.format_percentage(return_rate)
        }
        
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error calculating KPI data: {e}")
        return {}