import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataProcessor:
    """Класс для обработки и преобразования данных"""
    
    @staticmethod
    def safe_convert_date(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """Безопасное преобразование даты"""
        if df.empty or date_column not in df.columns:
            return df
            
        try:
            df[date_column] = pd.to_datetime(df[date_column])
        except Exception as e:
            logger.warning(f"Failed to convert {date_column}: {e}")
            
        return df
    
    @staticmethod
    def calculate_percentage_change(current: float, previous: float) -> float:
        """Рассчитать процентное изменение"""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def format_currency(value: float) -> str:
        """Форматирование валюты"""
        if value >= 1_000_000:
            return f"{(value / 1_000_000):.1f}M ₽"
        elif value >= 1_000:
            return f"{(value / 1_000):.1f}K ₽"
        else:
            return f"{value:,.0f} ₽"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Форматирование процентов"""
        return f"{value:.1f}%"
    
    @staticmethod
    def detect_anomalies(df: pd.DataFrame, value_column: str, threshold: float = 2.0) -> pd.DataFrame:
        """Обнаружение аномалий в данных"""
        if df.empty or value_column not in df.columns:
            return df
            
        mean = df[value_column].mean()
        std = df[value_column].std()
        
        if std > 0:
            df['is_anomaly'] = abs(df[value_column] - mean) > threshold * std
        else:
            df['is_anomaly'] = False
            
        return df

# Глобальный экземпляр процессора
data_processor = DataProcessor()