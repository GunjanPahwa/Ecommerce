SELECT 
    delay_bucket,
    COUNT(order_id) AS order_count,
    ROUND(AVG(CAST(review_score AS FLOAT)), 2) AS avg_review_score,
    ROUND(SUM(payment_value), 2) AS total_gmv
FROM (
    SELECT 
        order_id, 
        review_score, 
        payment_value,
        CASE 
            WHEN delivery_delay_days <= 0 THEN 'On-Time or Early'
            WHEN delivery_delay_days BETWEEN 1 AND 3 THEN 'Slightly Late (1-3 days)'
            WHEN delivery_delay_days BETWEEN 4 AND 7 THEN 'Moderately Late (4-7 days)'
            WHEN delivery_delay_days > 7 THEN 'Severely Late (7+ days)'
            ELSE 'Unknown/Incomplete Data' -- This catches actual missing values
        END AS delay_bucket
    FROM orders_master
) AS sub
GROUP BY delay_bucket
ORDER BY avg_review_score ASC;

SELECT 
    order_status, 
    COUNT(*) AS count 
FROM orders_master 
WHERE delivery_delay_days IS NULL 
GROUP BY order_status;