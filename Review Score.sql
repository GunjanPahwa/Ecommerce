SELECT 
    CASE WHEN is_late = 1 THEN 'Late' ELSE 'On-Time' END AS delivery_status,
    COUNT(order_id) AS order_count,
    AVG(CAST(review_score AS FLOAT)) AS avg_review_score
FROM orders_master
WHERE review_score IS NOT NULL
GROUP BY is_late;