SELECT TOP 20
    product_category,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(CAST(is_late AS FLOAT)) * 100, 2) AS late_rate_pct,
    ROUND(AVG(CAST(delivery_delay_days AS FLOAT)), 1) AS avg_delay_days,
    ROUND(AVG(CAST(review_score AS FLOAT)), 2) AS avg_review_score
FROM orders_master
WHERE product_category IS NOT NULL
GROUP BY product_category
HAVING COUNT(order_id) > 30
ORDER BY late_rate_pct DESC;