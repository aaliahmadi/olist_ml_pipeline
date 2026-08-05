# ============================================
# Model Training
# ============================================

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def train_model(session):
    """Train Random Forest model on customer features"""
    print('   [MODEL] Training model...')
    
    # Load data
    df = session.table("customer_features_with_label").to_pandas()
    print(f'   Loaded {len(df)} rows')
    
    # Prepare features
    target = 'IS_REPEAT'
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    features = [c for c in numeric_cols if c != target]
    
    X = df[features].fillna(0)
    y = df[target]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'   ✅ Accuracy: {accuracy:.4f}')
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print('   Top features:', importance.head(3)['feature'].tolist())
    
    return model, features, accuracy