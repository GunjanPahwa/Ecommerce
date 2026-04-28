SELECT TOP 10
    seller_id, 
    seller_city,
    COUNT(order_id) AS total_orders,
    SUM(CAST(is_late AS INT)) AS late_orders,
    ROUND(AVG(CAST(is_late AS FLOAT)) * 100, 2) AS late_delivery_rate
FROM orders_master
GROUP BY seller_id, seller_city
HAVING COUNT(order_id) > 50
ORDER BY late_delivery_rate DESC;