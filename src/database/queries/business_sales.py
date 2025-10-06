"""
SQL запросы для бизнес-аналитики и продаж
"""

# Основные KPI метрики
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

# Топ товаров
TOP_PRODUCTS_QUERY = """
SELECT 
    p.product_name,
    p.category,
    COUNT(s.transaction_id) as sales_count,
    SUM(s.quantity * p.price) as total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
WHERE s.transaction_date BETWEEN %(start_date)s AND %(end_date)s
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 15
"""