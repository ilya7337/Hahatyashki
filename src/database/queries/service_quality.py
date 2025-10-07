"""
SQL запросы для анализа качества обслуживания
"""

# Метрики поддержки
SUPPORT_METRICS_QUERY = """
SELECT 
    issue_type,
    COUNT(ticket_id) AS tickets_count,
    AVG(resolution_time_minutes) AS avg_resolution_time,
    COUNT(CASE WHEN resolved THEN 1 END) * 100.0 / COUNT(*) AS resolution_rate
FROM customer_support
WHERE support_date BETWEEN :start_date AND :end_date
  AND (:issue_type = 'all' OR issue_type = :issue_type)
GROUP BY issue_type
ORDER BY tickets_count DESC
"""

# Динамика обращений
SUPPORT_TREND_QUERY = """
SELECT 
    DATE(support_date) AS date,
    COUNT(ticket_id) AS daily_tickets,
    AVG(resolution_time_minutes) AS avg_resolution_time
FROM customer_support
WHERE support_date BETWEEN :start_date AND :end_date
  AND (:issue_type = 'all' OR issue_type = :issue_type)
  AND (:segment = 'all' OR customer_id IN (
        SELECT customer_id FROM user_segments WHERE segment = :segment
      ))
  AND (:region = 'all' OR customer_id IN (
        SELECT customer_id FROM user_segments WHERE region = :region
      ))
GROUP BY DATE(support_date)
ORDER BY date
"""

# Эффективность поддержки по сегментам
SEGMENT_SUPPORT_QUERY = """
SELECT 
    us.segment,
    COUNT(cs.ticket_id) AS tickets_count,
    AVG(cs.resolution_time_minutes) AS avg_resolution_time,
    COUNT(CASE WHEN cs.resolved THEN 1 END) * 100.0 / COUNT(*) AS resolution_rate
FROM customer_support cs
JOIN user_segments us ON cs.customer_id = us.customer_id
WHERE cs.support_date BETWEEN :start_date AND :end_date
  AND (:issue_type = 'all' OR cs.issue_type = :issue_type)
  AND (:segment = 'all' OR us.segment = :segment)
  AND (:region = 'all' OR us.region = :region)
GROUP BY us.segment
ORDER BY tickets_count DESC
"""

# Анализ времени решения
RESOLUTION_TIME_ANALYSIS_QUERY = """
SELECT 
    CASE 
        WHEN resolution_time_minutes < 60 THEN 'До 1 часа'
        WHEN resolution_time_minutes < 240 THEN '1-4 часа'
        WHEN resolution_time_minutes < 1440 THEN '4-24 часа'
        ELSE 'Более 24 часов'
    END AS resolution_time_bucket,
    COUNT(ticket_id) AS tickets_count,
    AVG(resolution_time_minutes) AS avg_resolution_time
FROM customer_support
WHERE support_date BETWEEN :start_date AND :end_date
  AND (:issue_type = 'all' OR issue_type = :issue_type)
  AND (:segment = 'all' OR customer_id IN (
        SELECT customer_id FROM user_segments WHERE segment = :segment
      ))
  AND (:region = 'all' OR customer_id IN (
        SELECT customer_id FROM user_segments WHERE region = :region
      ))
GROUP BY resolution_time_bucket
ORDER BY tickets_count DESC
"""

# Связь поддержки и возвратов
SUPPORT_RETURNS_CORRELATION_QUERY = """
SELECT 
    cs.issue_type,
    COUNT(DISTINCT cs.ticket_id) AS support_tickets,
    COUNT(DISTINCT r.return_id) AS returns_count,
    CASE 
        WHEN COUNT(DISTINCT cs.ticket_id) > 0 THEN 
            COUNT(DISTINCT r.return_id) * 100.0 / COUNT(DISTINCT cs.ticket_id)
        ELSE 0 
    END AS returns_per_ticket
FROM customer_support cs
LEFT JOIN returns r ON cs.customer_id = r.customer_id
  AND r.return_id IN (
      SELECT return_id FROM returns 
      WHERE EXISTS (
          SELECT 1 FROM sales s 
          WHERE s.transaction_id = returns.transaction_id 
            AND s.transaction_date BETWEEN :start_date AND :end_date
      )
  )
WHERE cs.support_date BETWEEN :start_date AND :end_date
  AND (:issue_type = 'all' OR cs.issue_type = :issue_type)
  AND (:segment = 'all' OR cs.customer_id IN (
        SELECT customer_id FROM user_segments WHERE segment = :segment
      ))
  AND (:region = 'all' OR cs.customer_id IN (
        SELECT customer_id FROM user_segments WHERE region = :region
      ))
GROUP BY cs.issue_type
ORDER BY support_tickets DESC
"""

# Удовлетворенность по регионам
REGIONAL_SUPPORT_QUERY = """
SELECT 
    us.region,
    COUNT(cs.ticket_id) AS tickets_count,
    AVG(cs.resolution_time_minutes) AS avg_resolution_time,
    COUNT(CASE WHEN cs.resolved THEN 1 END) * 100.0 / COUNT(*) AS resolution_rate
FROM customer_support cs
JOIN user_segments us ON cs.customer_id = us.customer_id
WHERE cs.support_date BETWEEN :start_date AND :end_date
  AND (:issue_type = 'all' OR cs.issue_type = :issue_type)
  AND (:segment = 'all' OR us.segment = :segment)
  AND (:region = 'all' OR us.region = :region)
GROUP BY us.region
ORDER BY tickets_count DESC
"""