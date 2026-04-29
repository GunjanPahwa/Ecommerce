SELECT 
    seller_city,
    SUM(payment_value) AS total_revenue,
    SUM(CASE WHEN is_late = 1 THEN payment_value ELSE 0 END) AS revenue_at_risk,
    ROUND((SUM(CASE WHEN is_late = 1 THEN payment_value ELSE 0 END) / SUM(payment_value)) * 100, 2) AS pct_revenue_at_risk
FROM orders_master
GROUP BY seller_city
HAVING COUNT(order_id) > 100
ORDER BY pct_revenue_at_risk DESC;