-- ============================================
-- UDF Creation (Alternative SQL-only approach)
-- ============================================

CREATE OR REPLACE FUNCTION predict_repeat(
    -- This would need all feature columns
    -- But we create it via Python instead
)
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

def predict(f0, f1, f2, f3, f4, f5, f6, f7, f8, f9):
    import_dir = sys._xoptions["snowflake_import_directory"]
    model = joblib.load(os.path.join(import_dir, 'churn_model.joblib'))
    features = [[f0, f1, f2, f3, f4, f5, f6, f7, f8, f9]]
    prob = model.predict_proba(features)[0][1]
    return float(prob)
$$;