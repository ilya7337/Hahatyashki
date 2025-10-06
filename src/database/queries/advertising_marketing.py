"""
SQL запросы для анализа рекламы и маркетинга
"""

# Эффективность кампаний
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
    END as roi,
    CASE 
        WHEN SUM(impressions) > 0 THEN SUM(clicks) * 100.0 / SUM(impressions)
        ELSE 0 
    END as ctr
FROM ad_revenue
WHERE date BETWEEN :start_date AND :end_date
GROUP BY campaign_name
ORDER BY roi DESC
"""

# Динамика рекламных показателей
AD_TREND_QUERY = """
SELECT 
    date,
    SUM(revenue) as daily_revenue,
    SUM(spend) as daily_spend,
    SUM(clicks) as daily_clicks,
    SUM(impressions) as daily_impressions
FROM ad_revenue
WHERE date BETWEEN :start_date AND :end_date
GROUP BY date
ORDER BY date
"""

# Эффективность по товарам
PRODUCT_AD_PERFORMANCE_QUERY = """
SELECT 
    p.product_name,
    p.category,
    SUM(ar.revenue) as total_revenue,
    SUM(ar.spend) as total_spend,
    SUM(ar.clicks) as total_clicks,
    CASE 
        WHEN SUM(ar.spend) > 0 THEN (SUM(ar.revenue) - SUM(ar.spend)) / SUM(ar.spend)
        ELSE 0 
    END as roi
FROM ad_revenue ar
JOIN products p ON ar.product_id = p.product_id
WHERE ar.date BETWEEN :start_date AND :end_date
GROUP BY p.product_id, p.product_name, p.category
ORDER BY roi DESC
LIMIT 15
"""

# Конверсия по каналам
CHANNEL_CONVERSION_QUERY = """
SELECT 
    t.channel,
    COUNT(DISTINCT t.traffic_id) as sessions,
    COUNT(DISTINCT s.transaction_id) as orders,
    CASE 
        WHEN COUNT(DISTINCT t.traffic_id) > 0 THEN 
            COUNT(DISTINCT s.transaction_id) * 100.0 / COUNT(DISTINCT t.traffic_id)
        ELSE 0 
    END as conversion_rate
FROM traffic t
LEFT JOIN sales s ON t.customer_id = s.customer_id
    AND s.transaction_date BETWEEN :start_date AND :end_date
WHERE t.session_start BETWEEN :start_date AND :end_date
GROUP BY t.channel
ORDER BY conversion_rate DESC
"""

# ROI по периодам
ROI_TREND_QUERY = """
SELECT 
    DATE_TRUNC('week', date) as week_start,
    SUM(revenue) as weekly_revenue,
    SUM(spend) as weekly_spend,
    CASE 
        WHEN SUM(spend) > 0 THEN (SUM(revenue) - SUM(spend)) / SUM(spend)
        ELSE 0 
    END as weekly_roi
FROM ad_revenue
WHERE date BETWEEN :start_date AND :end_date
GROUP BY week_start
ORDER BY week_start
"""

# Топ кампаний по CTR
TOP_CTR_CAMPAIGNS_QUERY = """
SELECT 
    campaign_name,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions,
    CASE 
        WHEN SUM(impressions) > 0 THEN SUM(clicks) * 100.0 / SUM(impressions)
        ELSE 0 
    END as ctr
FROM ad_revenue
WHERE date BETWEEN :start_date AND :end_date
GROUP BY campaign_name
HAVING SUM(impressions) > 1000
ORDER BY ctr DESC
LIMIT 10
"""