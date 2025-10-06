"""
SQL запросы для извлечения данных из PostgreSQL
"""

# Базовые запросы для проверки данных
CHECK_TABLES = """
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
"""

# KPI метрики
KPI_QUERY = """
SELECT 
    COUNT(DISTINCT s.transaction_id) as total_orders,
    SUM(s.quantity * p.price) as total_revenue,
    COUNT(DISTINCT r.return_id) as total_returns,
    AVG(s.quantity * p.price) as avg_order_value
FROM sales s
JOIN products p ON s.product_id = p.product_id
LEFT JOIN returns r ON s.transaction_id = r.transaction_id
WHERE s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
"""

# Динамика продаж
SALES_TREND_QUERY = """
SELECT 
    DATE(s.transaction_date) as date,
    COUNT(DISTINCT s.transaction_id) as orders_count,
    SUM(s.quantity * p.price) as daily_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
WHERE s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY DATE(s.transaction_date)
ORDER BY date
"""

# Продажи по категориям
CATEGORY_SALES_QUERY = """
SELECT 
    p.category,
    COUNT(DISTINCT s.transaction_id) as orders_count,
    SUM(s.quantity * p.price) as category_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
WHERE s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY p.category
ORDER BY category_revenue DESC
"""

# Воронка событий
EVENTS_FUNNEL_QUERY = """
SELECT 
    event_type,
    COUNT(DISTINCT event_id) as events_count
FROM events
WHERE event_timestamp BETWEEN %(start_date)s AND %(end_date)s
GROUP BY event_type
ORDER BY 
    CASE event_type
        WHEN 'view' THEN 1
        WHEN 'click' THEN 2
        WHEN 'add_to_cart' THEN 3
        WHEN 'wishlist' THEN 4
        WHEN 'purchase' THEN 5
        ELSE 6
    END
"""

# Сегментация пользователей
USER_SEGMENTS_QUERY = """
SELECT 
    segment,
    COUNT(DISTINCT customer_id) as users_count
FROM user_segments
GROUP BY segment
"""

# Эффективность рекламы
AD_PERFORMANCE_QUERY = """
SELECT 
    campaign_name,
    SUM(revenue) as total_revenue,
    SUM(spend) as total_spend,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions,
    CASE 
        WHEN SUM(spend) > 0 THEN (SUM(revenue) - SUM(spend)) / SUM(spend)
        ELSE 0 
    END as roi
FROM ad_revenue
WHERE date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY campaign_name
ORDER BY roi DESC
"""

# Анализ возвратов
RETURNS_ANALYSIS_QUERY = """
SELECT 
    r.reason,
    COUNT(r.return_id) as returns_count,
    COUNT(r.return_id) * 100.0 / (SELECT COUNT(*) FROM returns WHERE EXISTS (
        SELECT 1 FROM sales s 
        WHERE s.transaction_id = returns.transaction_id 
        AND s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
    )) as percentage
FROM returns r
WHERE EXISTS (
    SELECT 1 FROM sales s 
    WHERE s.transaction_id = r.transaction_id 
    AND s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
)
GROUP BY r.reason
ORDER BY returns_count DESC
"""

# Каналы трафика
TRAFFIC_CHANNELS_QUERY = """
SELECT 
    channel,
    COUNT(DISTINCT traffic_id) as sessions_count,
    COUNT(DISTINCT customer_id) as unique_users
FROM traffic
WHERE session_start BETWEEN %(start_date)s AND %(end_date)s
GROUP BY channel
ORDER BY sessions_count DESC
"""

# Остатки на складе
INVENTORY_STATUS_QUERY = """
SELECT 
    p.category,
    SUM(i.stock_quantity) as total_stock,
    COUNT(DISTINCT i.product_id) as unique_products,
    CASE 
        WHEN SUM(i.stock_quantity) = 0 THEN 'OUT_OF_STOCK'
        WHEN SUM(i.stock_quantity) < 10 THEN 'LOW_STOCK'
        ELSE 'IN_STOCK'
    END as stock_status
FROM inventory i
JOIN products p ON i.product_id = p.product_id
GROUP BY p.category
ORDER BY total_stock DESC
"""

# Метрики поддержки
SUPPORT_METRICS_QUERY = """
SELECT 
    issue_type,
    COUNT(ticket_id) as tickets_count,
    AVG(resolution_time_minutes) as avg_resolution_time,
    COUNT(CASE WHEN resolved THEN 1 END) * 100.0 / COUNT(*) as resolution_rate
FROM customer_support
WHERE support_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY issue_type
ORDER BY tickets_count DESC
"""

# Производительность поставщиков
SUPPLIER_PERFORMANCE_QUERY = """
SELECT 
    s.supplier_name,
    COUNT(DISTINCT sa.transaction_id) as orders_count,
    SUM(sa.quantity * p.price) as total_revenue,
    AVG(s.rating) as supplier_rating
FROM sales sa
JOIN products p ON sa.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE sa.transaction_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY s.supplier_name
ORDER BY total_revenue DESC
LIMIT 10
"""