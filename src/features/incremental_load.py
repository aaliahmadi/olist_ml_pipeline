# ============================================
# ETL: Incremental Load
# ============================================

from snowflake.snowpark.functions import col, max as spark_max, year, month, when, lit, expr

def run_incremental_load(session):
    """Load new orders incrementally from source to silver_orders"""
    print('   [ETL] Running incremental load...')
    
    # Get last load timestamp
    try:
        control_df = session.table("etl_control")
        last_load = control_df.select(spark_max("last_load_timestamp")).collect()[0][0]
        print(f'   Last load: {last_load}')
    except:
        # Create control table if it doesn't exist
        session.sql("""
            CREATE TABLE IF NOT EXISTS etl_control (
                pipeline_name STRING,
                last_load_timestamp TIMESTAMP,
                rows_loaded NUMBER
            )
        """).collect()
        
        session.sql("""
            INSERT INTO etl_control (pipeline_name, last_load_timestamp, rows_loaded)
            VALUES ('order_pipeline', '1900-01-01', 0)
        """).collect()
        last_load = None
        print('   No previous load found. Doing full load.')
    
    # Get new orders
    if last_load:
        new_orders = session.table("olist_orders") \
            .filter(col("order_purchase_timestamp") > last_load)
    else:
        new_orders = session.table("olist_orders")
    
    new_count = new_orders.count()
    print(f'   Found {new_count} new orders')
    
    if new_count > 0:
        # Clean and transform
        new_orders_clean = new_orders \
            .filter(col("order_id").isNotNull()) \
            .filter(col("customer_id").isNotNull()) \
            .with_column("order_year", year(col("order_purchase_timestamp"))) \
            .with_column("order_month", month(col("order_purchase_timestamp"))) \
            .with_column("is_delivered", when(col("order_status") == "delivered", lit(1)).otherwise(lit(0))) \
            .with_column("is_canceled", when(col("order_status") == "canceled", lit(1)).otherwise(lit(0))) \
            .with_column("delivery_days", expr("DATEDIFF(day, order_purchase_timestamp, order_delivered_customer_date)"))
        
        # Create temp table
        new_orders_clean.write.mode("overwrite").save_as_table("TEMP_NEW_ORDERS")
        
        # Merge into silver_orders
        try:
            merge_sql = """
                MERGE INTO silver_orders AS target
                USING (SELECT * FROM TEMP_NEW_ORDERS) AS source
                ON target.order_id = source.order_id
                WHEN MATCHED THEN UPDATE SET
                    target.order_status = source.order_status,
                    target.order_purchase_timestamp = source.order_purchase_timestamp,
                    target.order_delivered_customer_date = source.order_delivered_customer_date,
                    target.delivery_days = source.delivery_days,
                    target.is_delivered = source.is_delivered,
                    target.is_canceled = source.is_canceled
                WHEN NOT MATCHED THEN INSERT (
                    order_id, customer_id, order_status, order_purchase_timestamp,
                    order_approved_at, order_delivered_carrier_date, order_delivered_customer_date,
                    order_estimated_delivery_date, order_year, order_month,
                    is_delivered, is_canceled, delivery_days
                ) VALUES (
                    source.order_id, source.customer_id, source.order_status, source.order_purchase_timestamp,
                    source.order_approved_at, source.order_delivered_carrier_date, source.order_delivered_customer_date,
                    source.order_estimated_delivery_date, source.order_year, source.order_month,
                    source.is_delivered, source.is_canceled, source.delivery_days
                )
            """
            session.sql(merge_sql).collect()
        except:
            # If silver_orders doesn't exist, create it
            new_orders_clean.write.mode("overwrite").save_as_table("silver_orders")
        
        # Update control table
        new_max = new_orders.select(spark_max("order_purchase_timestamp")).collect()[0][0]
        session.sql(f"""
            UPDATE etl_control
            SET last_load_timestamp = '{new_max}',
                rows_loaded = rows_loaded + {new_count}
            WHERE pipeline_name = 'order_pipeline'
        """).collect()
        
        # Cleanup
        session.sql("DROP TABLE IF EXISTS TEMP_NEW_ORDERS").collect()
        
        print(f'   ✅ Loaded {new_count} new orders')
        return new_count
    else:
        print('   ✅ No new orders to load')
        return 0