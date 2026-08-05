# ============================================
# Model Prediction & Scoring
# ============================================

import joblib
import os
import sys

def deploy_udf(session, model, features):
    """Deploy model as UDF for real-time scoring"""
    print('   [DEPLOY] Creating prediction UDF...')
    
    # Save model locally
    os.makedirs('/tmp/models', exist_ok=True)
    model_path = '/tmp/models/churn_model.joblib'
    joblib.dump(model, model_path)
    
    # Upload to stage
    session.sql("CREATE OR REPLACE STAGE model_stage").collect()
    session.file.put(model_path, '@model_stage', overwrite=True, auto_compress=False)
    
    # Create UDF
    param_defs = ", ".join([f"f{i} FLOAT" for i in range(len(features))])
    param_names = ", ".join([f"f{i}" for i in range(len(features))])
    
    udf_sql = f"""
    CREATE OR REPLACE FUNCTION predict_repeat({param_defs})
    RETURNS FLOAT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.10'
    PACKAGES = ('scikit-learn', 'joblib', 'pandas')
    IMPORTS = ('@model_stage/churn_model.joblib')
    HANDLER = 'predict'
    AS
    $$
    import joblib
    import sys
    import os

    def predict({param_names}):
        import_dir = sys._xoptions["snowflake_import_directory"]
        model = joblib.load(os.path.join(import_dir, 'churn_model.joblib'))
        features = [[{param_names}]]
        prob = model.predict_proba(features)[0][1]
        return float(prob)
    $$;
    """
    
    session.sql(udf_sql).collect()
    print('   ✅ UDF created successfully')
    
    return True

def score_customers(session, features):
    """Score all customers using the UDF"""
    print('   [SCORE] Scoring all customers...')
    
    feature_sql_args = ", ".join([f'"{f}"' for f in features])
    
    scoring_query = f"""
    CREATE OR REPLACE TABLE customer_repeat_scores AS
    SELECT 
        customer_unique_id,
        customer_id,
        customer_state,
        predict_repeat({feature_sql_args}) AS repeat_score
    FROM customer_features_with_label
    """
    
    session.sql(scoring_query).collect()
    
    count = session.table("customer_repeat_scores").count()
    print(f'   ✅ Scored {count:,} customers')
    
    return count