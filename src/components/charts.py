import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List, Optional

class ChartBuilder:
    """Класс для построения графиков"""
    
    @staticmethod
    def create_sales_trend_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график динамики продаж"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Линия заказов
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['orders_count'],
                name="Количество заказов",
                line=dict(color='#3498DB', width=3),
                mode='lines+markers'
            ),
            secondary_y=False
        )
        
        # Линия выручки
        fig.add_trace(
            go.Scatter(
                x=data['date'], 
                y=data['daily_revenue'],
                name="Выручка",
                line=dict(color='#27AE60', width=3),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Динамика продаж и выручки",
            xaxis_title="Дата",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_yaxes(title_text="Количество заказов", secondary_y=False)
        fig.update_yaxes(title_text="Выручка (руб)", secondary_y=True)
        
        return fig
    
    @staticmethod
    def create_category_sales_chart(data: pd.DataFrame) -> go.Figure:
        """Создать круговую диаграмму продаж по категориям"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = px.pie(
            data, 
            values='category_revenue', 
            names='category',
            title='Распределение продаж по категориям',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Выручка: %{value:,.0f} руб<br>Доля: %{percent}'
        )
        
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.1
            )
        )
        
        return fig
    
    @staticmethod
    def create_funnel_chart(data: pd.DataFrame) -> go.Figure:
        """Создать воронку событий"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        # Сортируем по порядку воронки
        event_order = ['view', 'click', 'add_to_cart', 'wishlist', 'purchase', 'search']
        data['event_type'] = pd.Categorical(data['event_type'], categories=event_order, ordered=True)
        data = data.sort_values('event_type')
        
        fig = px.funnel(
            data, 
            x='events_count', 
            y='event_type',
            title='Воронка событий пользователей',
            labels={'events_count': 'Количество событий', 'event_type': 'Тип события'}
        )
        
        return fig
    
    @staticmethod
    def create_segmentation_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график сегментации пользователей"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = px.pie(
            data, 
            values='users_count', 
            names='segment',
            title='Распределение пользователей по сегментам',
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    @staticmethod
    def create_ad_performance_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график эффективности рекламы"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=('ROI по кампаниям', 'Расходы vs Доходы'))
        
        # ROI
        fig.add_trace(
            go.Bar(
                x=data['campaign_name'],
                y=data['roi'],
                name="ROI",
                marker_color='#E74C3C'
            ),
            row=1, col=1
        )
        
        # Расходы и доходы
        fig.add_trace(
            go.Bar(
                x=data['campaign_name'],
                y=data['total_spend'],
                name="Расходы",
                marker_color='#F39C12'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=data['campaign_name'],
                y=data['total_revenue'],
                name="Доходы",
                marker_color='#27AE60'
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=True)
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    @staticmethod
    def create_returns_analysis_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график анализа возвратов"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = px.bar(
            data,
            x='returns_count',
            y='reason',
            orientation='h',
            title='Анализ причин возвратов',
            labels={'returns_count': 'Количество возвратов', 'reason': 'Причина'},
            color='returns_count',
            color_continuous_scale='Reds'
        )
        
        return fig
    
    @staticmethod
    def create_traffic_channels_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график каналов трафика"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = px.sunburst(
            data,
            path=['channel'],
            values='sessions_count',
            title='Распределение трафика по каналам',
            color='sessions_count',
            color_continuous_scale='Blues'
        )
        
        return fig
    
    @staticmethod
    def create_inventory_status_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график статуса запасов"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = px.treemap(
            data,
            path=['category'],
            values='total_stock',
            title='Остатки товаров на складе по категориям',
            color='total_stock',
            color_continuous_scale='Greens'
        )
        
        return fig
    
    @staticmethod
    def create_support_metrics_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график метрик поддержки"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Типы обращений', 'Время решения'))
        
        # Количество тикетов по типам
        fig.add_trace(
            go.Bar(
                x=data['issue_type'],
                y=data['tickets_count'],
                name="Количество тикетов",
                marker_color='#9B59B6'
            ),
            row=1, col=1
        )
        
        # Время решения
        fig.add_trace(
            go.Bar(
                x=data['issue_type'],
                y=data['avg_resolution_time'],
                name="Ср. время решения (мин)",
                marker_color='#3498DB'
            ),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    @staticmethod
    def create_supplier_performance_chart(data: pd.DataFrame) -> go.Figure:
        """Создать график производительности поставщиков"""
        if data.empty:
            return go.Figure().update_layout(title="Нет данных")
        
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
            size_max=60
        )
        
        return fig

# Глобальный экземпляр построителя графиков
chart_builder = ChartBuilder()