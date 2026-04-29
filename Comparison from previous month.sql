SELECT 
    month,
    late_rate_pct,
    LAG(late_rate_pct) OVER (ORDER BY month) AS prev_month_rate,
    ROUND(late_rate_pct - LAG(late_rate_pct) OVER (ORDER BY month), 2) AS mom_change
FROM (
    SELECT 
        FORMAT(CAST(order_purchase_timestamp AS DATETIME), 'yyyy-MM') AS [month],
        ROUND(AVG(CAST(is_late AS FLOAT)) * 100, 2) AS late_rate_pct
    FROM orders_master
    WHERE order_purchase_timestamp IS NOT NULL
    GROUP BY FORMAT(CAST(order_purchase_timestamp AS DATETIME), 'yyyy-MM')
) AS monthly_stats
ORDER BY month;