"""
Общие SQL запросы для всех страниц
"""

# Категории товаров
CATEGORIES_QUERY = """
SELECT DISTINCT category 
FROM products 
WHERE category IS NOT NULL 
ORDER BY category
"""

# Сегменты пользователей
SEGMENTS_QUERY = """
SELECT DISTINCT segment 
FROM user_segments 
WHERE segment IS NOT NULL 
ORDER BY segment
"""

# Каналы трафика
CHANNELS_QUERY = """
SELECT DISTINCT channel 
FROM traffic 
WHERE channel IS NOT NULL 
ORDER BY channel
"""

# Регионы
REGIONS_QUERY = """
SELECT DISTINCT region 
FROM user_segments 
WHERE region IS NOT NULL 
ORDER BY region
"""

# Поставщики
SUPPLIERS_QUERY = """
SELECT DISTINCT supplier_name 
FROM suppliers 
WHERE supplier_name IS NOT NULL 
ORDER BY supplier_name
"""