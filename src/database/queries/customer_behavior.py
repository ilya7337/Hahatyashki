# Сегментация пользователей
USER_SEGMENTS_QUERY = """
SELECT 
    us.segment,
    COUNT(DISTINCT us.customer_id) AS users_count
FROM user_segments us
LEFT JOIN sales s ON us.customer_id = s.customer_id
LEFT JOIN products p ON s.product_id = p.product_id
LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
WHERE (:segment IS NULL OR us.segment = :segment)
  AND (:region IS NULL OR us.region = :region)
  AND (:supplier IS NULL OR sp.supplier_name = :supplier)
GROUP BY us.segment;
"""

# Воронка событий
EVENTS_FUNNEL_QUERY = """
WITH filtered_users AS (
    SELECT DISTINCT us.customer_id
    FROM user_segments us
    LEFT JOIN sales s ON us.customer_id = s.customer_id
    LEFT JOIN products p ON s.product_id = p.product_id
    LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
    WHERE (:segment IS NULL OR us.segment = :segment)
      AND (:region IS NULL OR us.region = :region)
      AND (:supplier IS NULL OR sp.supplier_name = :supplier)
)
SELECT 
    e.event_type,
    COUNT(e.event_id) AS events_count
FROM events e
JOIN filtered_users u ON e.customer_id = u.customer_id
WHERE e.event_timestamp BETWEEN :start_date AND :end_date
GROUP BY e.event_type
ORDER BY 
    CASE e.event_type
        WHEN 'view' THEN 1
        WHEN 'click' THEN 2
        WHEN 'add_to_cart' THEN 3
        WHEN 'wishlist' THEN 4
        WHEN 'purchase' THEN 5
        ELSE 6
    END;
"""

# Активность по регионам
REGIONAL_ACTIVITY_QUERY = """
SELECT 
    us.region,
    COUNT(DISTINCT us.customer_id) AS total_users,
    COUNT(DISTINCT s.transaction_id) AS total_orders,
    COUNT(s.transaction_id) * 1.0 / COUNT(DISTINCT us.customer_id) AS orders_per_user
FROM user_segments us
LEFT JOIN sales s
    ON us.customer_id = s.customer_id
   AND s.transaction_date BETWEEN :start_date AND :end_date
LEFT JOIN products p ON s.product_id = p.product_id
LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
WHERE (:segment IS NULL OR us.segment = :segment)
  AND (:region IS NULL OR us.region = :region)
  AND (:supplier IS NULL OR sp.supplier_name = :supplier)
GROUP BY us.region
ORDER BY total_orders DESC;
"""

# Поведение сегментов
SEGMENT_BEHAVIOR_QUERY = """
SELECT 
    us.segment,
    COUNT(s.transaction_id) AS total_orders,
    AVG(s.quantity * p.price) AS avg_order_value,
    COUNT(r.return_id) AS total_returns
FROM user_segments us
LEFT JOIN sales s
    ON us.customer_id = s.customer_id
   AND s.transaction_date BETWEEN :start_date AND :end_date
LEFT JOIN products p
    ON s.product_id = p.product_id
LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
LEFT JOIN returns r
    ON s.transaction_id = r.transaction_id
WHERE (:segment IS NULL OR us.segment = :segment)
  AND (:region IS NULL OR us.region = :region)
  AND (:supplier IS NULL OR sp.supplier_name = :supplier)
GROUP BY us.segment
ORDER BY total_orders DESC;
"""

# Каналы трафика
TRAFFIC_CHANNELS_QUERY = """
WITH filtered_users AS (
    SELECT DISTINCT us.customer_id
    FROM user_segments us
    LEFT JOIN sales s ON us.customer_id = s.customer_id
    LEFT JOIN products p ON s.product_id = p.product_id
    LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
    WHERE (:segment IS NULL OR us.segment = :segment)
      AND (:region IS NULL OR us.region = :region)
      AND (:supplier IS NULL OR sp.supplier_name = :supplier)
)
SELECT 
    t.channel,
    COUNT(t.traffic_id) AS sessions_count,
    COUNT(DISTINCT t.customer_id) AS unique_users
FROM traffic t
JOIN filtered_users u ON t.customer_id = u.customer_id
WHERE t.session_start BETWEEN :start_date AND :end_date
GROUP BY t.channel
ORDER BY sessions_count DESC;
"""

# Устройства пользователей
USER_DEVICES_QUERY = """
WITH filtered_users AS (
    SELECT DISTINCT us.customer_id
    FROM user_segments us
    LEFT JOIN sales s ON us.customer_id = s.customer_id
    LEFT JOIN products p ON s.product_id = p.product_id
    LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
    WHERE (:segment IS NULL OR us.segment = :segment)
      AND (:region IS NULL OR us.region = :region)
      AND (:supplier IS NULL OR sp.supplier_name = :supplier)
)
SELECT 
    t.device,
    COUNT(t.traffic_id) AS sessions_count,
    COUNT(DISTINCT t.customer_id) AS unique_users
FROM traffic t
JOIN filtered_users u ON t.customer_id = u.customer_id
WHERE t.session_start BETWEEN :start_date AND :end_date
GROUP BY t.device
ORDER BY sessions_count DESC;
"""

# Лояльность клиентов
CUSTOMER_LOYALTY_QUERY = """
WITH customer_orders AS (
    SELECT
        us.customer_id,
        COUNT(s.transaction_id) AS orders_count,
        AVG(s.quantity * p.price) AS avg_order_value
    FROM user_segments us
    LEFT JOIN sales s
        ON us.customer_id = s.customer_id
       AND s.transaction_date BETWEEN :start_date AND :end_date
    LEFT JOIN products p
        ON s.product_id = p.product_id
    LEFT JOIN suppliers sp ON p.supplier_id = sp.supplier_id
    WHERE (:segment IS NULL OR us.segment = :segment)
      AND (:region IS NULL OR us.region = :region)
      AND (:supplier IS NULL OR sp.supplier_name = :supplier)
    GROUP BY us.customer_id
)
SELECT
    CASE
        WHEN orders_count >= 5 THEN 'VIP'
        WHEN orders_count >= 3 THEN 'Постоянный'
        WHEN orders_count >= 1 THEN 'Новый'
        ELSE 'Неактивный'
    END AS loyalty_level,
    COUNT(*) AS customers_count,
    AVG(avg_order_value) AS avg_order_value
FROM customer_orders
GROUP BY loyalty_level
ORDER BY customers_count DESC;
"""