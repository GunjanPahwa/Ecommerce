SELECT TOP 20
    seller_id,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(payment_value), 2) AS total_gmv,
    ROUND(AVG(CAST(is_late AS FLOAT)) * 100, 2) AS late_rate_pct,
    ROUND(SUM(CASE WHEN is_late = 1 THEN payment_value ELSE 0 END), 2) AS gmv_at_risk,
    RANK() OVER (ORDER BY SUM(CASE WHEN is_late = 1 THEN payment_value ELSE 0 END) DESC) AS risk_rank
FROM orders_master
GROUP BY seller_id
HAVING COUNT(order_id) > 50
ORDER BY gmv_at_risk DESC;