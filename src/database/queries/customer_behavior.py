"""
SQL запросы для анализа клиентов и поведения
"""

# Сегментация пользователей
USER_SEGMENTS_QUERY = """
SELECT 
    segment,
    COUNT(DISTINCT customer_id) as users_count
FROM user_segments
GROUP BY segment
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

# Активность по регионам
REGIONAL_ACTIVITY_QUERY = """
SELECT 
    us.region,
    COUNT(DISTINCT us.customer_id) as total_users,
    COUNT(DISTINCT s.transaction_id) as total_orders,
    COUNT(DISTINCT s.transaction_id) * 1.0 / COUNT(DISTINCT us.customer_id) as orders_per_user
FROM user_segments us
LEFT JOIN sales s ON us.customer_id = s.customer_id
    AND s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY us.region
ORDER BY total_orders DESC
"""

# Поведение сегментов
SEGMENT_BEHAVIOR_QUERY = """
SELECT 
    us.segment,
    COUNT(DISTINCT s.transaction_id) as total_orders,
    AVG(s.quantity * p.price) as avg_order_value,
    COUNT(DISTINCT r.return_id) as total_returns
FROM user_segments us
LEFT JOIN sales s ON us.customer_id = s.customer_id
    AND s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
LEFT JOIN products p ON s.product_id = p.product_id
LEFT JOIN returns r ON s.transaction_id = r.transaction_id
GROUP BY us.segment
ORDER BY total_orders DESC
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

# Устройства пользователей
USER_DEVICES_QUERY = """
SELECT 
    device,
    COUNT(DISTINCT traffic_id) as sessions_count,
    COUNT(DISTINCT customer_id) as unique_users
FROM traffic
WHERE session_start BETWEEN %(start_date)s AND %(end_date)s
GROUP BY device
ORDER BY sessions_count DESC
"""

# Лояльность клиентов
CUSTOMER_LOYALTY_QUERY = """
SELECT 
    CASE 
        WHEN COUNT(DISTINCT s.transaction_id) >= 5 THEN 'VIP'
        WHEN COUNT(DISTINCT s.transaction_id) >= 3 THEN 'Постоянный'
        WHEN COUNT(DISTINCT s.transaction_id) >= 1 THEN 'Новый'
        ELSE 'Неактивный'
    END as loyalty_level,
    COUNT(DISTINCT us.customer_id) as customers_count,
    AVG(s.quantity * p.price) as avg_order_value
FROM user_segments us
LEFT JOIN sales s ON us.customer_id = s.customer_id
    AND s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
LEFT JOIN products p ON s.product_id = p.product_id
GROUP BY loyalty_level
ORDER BY customers_count DESC
"""