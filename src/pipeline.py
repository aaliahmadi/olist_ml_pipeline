# ============================================
# MAIN PIPELINE ORCHESTRATOR
# ============================================

import snowflake.snowpark as snowpark
from snowflake.snowpark.context import get_active_session
from etl.incremental_load import run_incremental_load
from features.first_order_features import create_first_order_features
from model.train_model import train_model
from model.predict import deploy_udf, score_customers

def run_full_pipeline(session):
    """Execute the complete end-to-end pipeline"""
    print('\n' + '='*60)
    print('[PIPELINE] Running Full Pipeline')
    print('='*60)
    
    # Step 1: Incremental ETL
    print('\n[STEP 1] Incremental Load')
    print('-'*40)
    new_orders = run_incremental_load(session)
    
    # Step 2: Feature Engineering
    print('\n[STEP 2] Feature Engineering')
    print('-'*40)
    feature_count = create_first_order_features(session)
    
    # Step 3: Train Model
    print('\n[STEP 3] Model Training')
    print('-'*40)
    model, features, accuracy = train_model(session)
    
    # Step 4: Deploy UDF
    print('\n[STEP 4] Model Deployment')
    print('-'*40)
    deploy_udf(session, model, features)
    
    # Step 5: Score Customers
    print('\n[STEP 5] Customer Scoring')
    print('-'*40)
    scored_count = score_customers(session, features)
    
    # Step 6: Daily Sales Summary
    print('\n[STEP 6] Dashboard Update')
    print('-'*40)
    session.sql("""
        CREATE OR REPLACE TABLE daily_sales_summary AS
        SELECT 
            DATE(order_purchase_timestamp) AS sale_date,
            COUNT(*) AS orders,
            SUM(oi.price) AS total_sales
        FROM silver_orders s
        JOIN olist_order_items oi ON s.order_id = oi.order_id
        GROUP BY sale_date
        ORDER BY sale_date DESC
    """).collect()
    print('   ✅ Daily sales summary updated')
    
    # Step 7: Weekly Summary
    print('\n[STEP 7] Weekly Summary')
    print('-'*40)
    summary = session.sql("""
        SELECT 
            COUNT(DISTINCT customer_id) AS unique_customers,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN is_delivered = 1 THEN 1 ELSE 0 END) AS delivered
        FROM silver_orders
        WHERE order_purchase_timestamp >= CURRENT_DATE - INTERVAL '7 days'
    """).collect()[0]
    
    print(f'   📊 Weekly Summary:')
    print(f'      Unique Customers: {summary["UNIQUE_CUSTOMERS"]:,}')
    print(f'      Total Orders: {summary["TOTAL_ORDERS"]:,}')
    print(f'      Delivered: {summary["DELIVERED"]:,}')
    
    # Final summary
    print('\n' + '='*60)
    print('[PIPELINE] ✅ Pipeline Completed Successfully!')
    print('='*60)
    print(f'   📦 New orders loaded: {new_orders}')
    print(f'   📊 Features created: {feature_count:,} rows')
    print(f'   🎯 Model accuracy: {accuracy:.4f}')
    print(f'   🏷️ Customers scored: {scored_count:,}')
    print('='*60)
    
    return True

# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    session = get_active_session()
    session.sql("USE DATABASE ALIM_DB").collect()
    session.sql("USE SCHEMA ALIM_DB.ALIM_SCHEMA").collect()
    
    run_full_pipeline(session)
    
    print('\n🎉 Congratulations! You have completed the 14-day course!')