# ============================================
# Feature Engineering: First Order Features
# ============================================

def create_first_order_features(session):
    """Create features from first order only (prevents data leakage)"""
    print('   [FEATURES] Creating first order features...')
    
    # This is the SQL from your Day 10.sql file
    sql = """
    CREATE OR REPLACE TABLE customer_features_with_label AS
    
    WITH customer_first_order AS (
        SELECT 
            c.customer_unique_id,
            c.customer_id,
            MIN(o.order_purchase_timestamp) AS first_order_date
        FROM olist_customers c
        JOIN olist_orders o ON c.customer_id = o.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id, c.customer_id
    ),
    
    first_order_features AS (
        SELECT 
            c.customer_unique_id,
            c.customer_id,
            c.customer_city,
            c.customer_state,
            cfo.first_order_date,
            DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS first_order_delivery_days,
            COUNT(DISTINCT oi.order_item_id) AS first_order_items_count,
            SUM(oi.price) AS first_order_total_spend,
            AVG(oi.price) AS first_order_avg_item_price,
            SUM(oi.freight_value) AS first_order_total_freight,
            MAX(op.payment_type) AS first_order_payment_type,
            MAX(op.payment_installments) AS first_order_payment_installments
        FROM olist_customers c
        JOIN customer_first_order cfo ON c.customer_unique_id = cfo.customer_unique_id
        JOIN olist_orders o ON c.customer_id = o.customer_id AND o.order_purchase_timestamp = cfo.first_order_date
        LEFT JOIN olist_order_items oi ON o.order_id = oi.order_id
        LEFT JOIN olist_order_payments op ON o.order_id = op.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY 
            c.customer_unique_id, 
            c.customer_id,
            c.customer_city,
            c.customer_state,
            cfo.first_order_date,
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
    ),
    
    customer_repeat_label AS (
        SELECT 
            c.customer_unique_id,
            CASE 
                WHEN COUNT(o.order_id) > 1 THEN 1 
                ELSE 0 
            END AS IS_REPEAT
        FROM olist_customers c
        JOIN customer_first_order cfo ON c.customer_unique_id = cfo.customer_unique_id
        LEFT JOIN olist_orders o ON c.customer_id = o.customer_id 
            AND o.order_purchase_timestamp > cfo.first_order_date
            AND o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
    )
    
    SELECT 
        f.customer_unique_id,
        f.customer_id,
        f.customer_city,
        f.customer_state,
        f.first_order_date,
        f.first_order_delivery_days,
        f.first_order_items_count,
        f.first_order_total_spend,
        f.first_order_avg_item_price,
        f.first_order_total_freight,
        f.first_order_payment_type,
        f.first_order_payment_installments,
        COALESCE(r.IS_REPEAT, 0) AS IS_REPEAT
    FROM first_order_features f
    LEFT JOIN customer_repeat_label r ON f.customer_unique_id = r.customer_unique_id
    """
    
    session.sql(sql).collect()
    
    # Verify
    count = session.table("customer_features_with_label").count()
    print(f'   ✅ Created features table with {count:,} rows')
    
    return count