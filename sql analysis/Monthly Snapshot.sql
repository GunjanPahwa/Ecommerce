SELECT 
    FORMAT(CAST(order_purchase_timestamp AS DATETIME), 'yyyy-MM') AS [month],
    COUNT(order_id) AS total_orders,
    SUM(CAST(is_late AS INT)) AS late_orders,
    ROUND(AVG(CAST(is_late AS FLOAT)) * 100, 2) AS late_rate_pct
FROM orders_master
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY FORMAT(CAST(order_purchase_timestamp AS DATETIME), 'yyyy-MM')
ORDER BY [month];

