SELECT 
    customer_state,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(CAST(is_late AS FLOAT)) * 100, 2) AS late_rate_pct,
    ROUND(AVG(delivery_delay_days), 1) AS avg_delay_days,
    ROUND(AVG(CAST(review_score AS FLOAT)), 2) AS avg_review_score,
    ROUND(AVG(freight_value), 2) AS avg_freight_cost
FROM orders_master
WHERE customer_state IS NOT NULL
GROUP BY customer_state
HAVING COUNT(order_id) > 50
ORDER BY late_rate_pct DESC;