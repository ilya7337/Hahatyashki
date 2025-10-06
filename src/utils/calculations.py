import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MetricCalculator:
    """Класс для расчета бизнес-метрик"""
    
    @staticmethod
    def calculate_conversion_rate(events_data: pd.DataFrame) -> Dict[str, float]:
        """Рассчитать коэффициенты конверсии воронки"""
        if events_data.empty:
            return {}
        
        event_counts = events_data.groupby('event_type')['events_count'].sum().to_dict()
        
        conversions = {}
        if event_counts.get('view', 0) > 0:
            conversions['view_to_click'] = event_counts.get('click', 0) / event_counts['view']
            conversions['click_to_cart'] = event_counts.get('add_to_cart', 0) / event_counts.get('click', 1)
            conversions['cart_to_purchase'] = event_counts.get('purchase', 0) / event_counts.get('add_to_cart', 1)
            conversions['overall_conversion'] = event_counts.get('purchase', 0) / event_counts['view']
        
        return conversions
    
    @staticmethod
    def calculate_customer_lifetime_value(sales_data: pd.DataFrame, users_data: pd.DataFrame) -> float:
        """Рассчитать LTV (Lifetime Value)"""
        if sales_data.empty or users_data.empty:
            return 0.0
        
        try:
            total_revenue = sales_data['daily_revenue'].sum()
            unique_customers = users_data['users_count'].sum()
            
            return total_revenue / unique_customers if unique_customers > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating LTV: {e}")
            return 0.0
    
    @staticmethod
    def calculate_retention_rate(users_data: pd.DataFrame, segments_data: pd.DataFrame) -> float:
        """Рассчитать коэффициент удержания"""
        if users_data.empty or segments_data.empty:
            return 0.0
        
        try:
            loyal_users = segments_data[segments_data['segment'] == 'loyal']['users_count'].sum()
            total_users = segments_data['users_count'].sum()
            
            return loyal_users / total_users if total_users > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating retention rate: {e}")
            return 0.0
    
    @staticmethod
    def forecast_sales(sales_data: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """Прогнозирование продаж на основе исторических данных"""
        if sales_data.empty:
            return pd.DataFrame()
        
        try:
            # Простое прогнозирование на основе скользящего среднего
            sales_data = sales_data.set_index('date')
            forecast = sales_data['orders_count'].rolling(window=7).mean().iloc[-1]
            
            # Создание прогноза на будущие периоды
            last_date = sales_data.index.max()
            forecast_dates = [last_date + timedelta(days=i) for i in range(1, periods + 1)]
            forecast_values = [forecast * (0.95 + 0.1 * np.random.random()) for _ in range(periods)]
            
            return pd.DataFrame({
                'date': forecast_dates,
                'forecast': forecast_values
            })
        except Exception as e:
            logger.error(f"Error forecasting sales: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def detect_seasonality(sales_data: pd.DataFrame) -> Dict[str, Any]:
        """Обнаружение сезонности в данных о продажах"""
        if sales_data.empty:
            return {}
        
        try:
            sales_data = sales_data.set_index('date')
            weekly_pattern = sales_data['orders_count'].groupby(sales_data.index.dayofweek).mean()
            monthly_pattern = sales_data['orders_count'].groupby(sales_data.index.day).mean()
            
            return {
                'weekly_peak_day': weekly_pattern.idxmax(),
                'weekly_peak_value': weekly_pattern.max(),
                'monthly_peak_day': monthly_pattern.idxmax(),
                'monthly_peak_value': monthly_pattern.max()
            }
        except Exception as e:
            logger.error(f"Error detecting seasonality: {e}")
            return {}

# Глобальный экземпляр калькулятора
metric_calculator = MetricCalculator()