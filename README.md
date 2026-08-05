# 🛒 Olist ML Pipeline - Customer Repeat Purchase Prediction

[![Snowflake](https://img.shields.io/badge/Snowflake-56B9EB?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)

An end-to-end data science pipeline built on **Snowflake** that predicts whether a customer will make a repeat purchase based on their first-order behavior.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Business Problem](#business-problem)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [How It Works](#how-it-works)
- [Key Features](#key-features)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project demonstrates a complete **ML pipeline** running entirely on Snowflake. It predicts customer repeat purchases using features derived from the customer's **first order only** — preventing data leakage and ensuring realistic predictions.

### What This Pipeline Does

| Step | Description |
|------|-------------|
| **1. Incremental ETL** | Loads new orders daily into a cleaned `silver_orders` table |
| **2. Feature Engineering** | Builds customer features from first-order behavior |
| **3. Model Training** | Trains a Random Forest classifier to predict repeat purchases |
| **4. Model Deployment** | Deploys the model as a Snowflake UDF (User-Defined Function) |
| **5. Batch Scoring** | Scores all customers and segments them by repeat probability |
| **6. Dashboard Updates** | Creates daily sales summaries and weekly reports |

---

## 💼 Business Problem

**Goal**: Identify customers likely to make repeat purchases based on their first interaction with the platform.

**Why It Matters**:
- 🎯 **Targeted Marketing** - Focus retention efforts on high-value customers
- 📈 **Revenue Growth** - Increase customer lifetime value (LTV)
- 🛡️ **Churn Prevention** - Identify at-risk customers early

**Key Insight**: The model uses **only first-order data** to make predictions, simulating a real-world scenario where we want to predict future behavior based on initial engagement.

---

## 📊 Dataset

The project uses the **Brazilian E-Commerce Olist Dataset**, which contains ~100,000 orders from 2016-2018.

### Key Tables

| Table | Rows | Description |
|-------|------|-------------|
| `olist_customers` | 99,441 | Customer demographics |
| `olist_orders` | 99,441 | Order information |
| `olist_order_items` | 112,650 | Line items per order |
| `olist_order_payments` | 103,886 | Payment details |
| `olist_order_reviews` | 99,224 | Customer reviews |
| `olist_products` | 32,951 | Product catalog |
| `olist_sellers` | 3,095 | Seller information |

### Feature Engineering

Features are derived **exclusively from the first order**:

- `first_order_delivery_days` - Delivery time
- `first_order_items_count` - Number of items
- `first_order_total_spend` - Total spend
- `first_order_avg_item_price` - Average item price
- `first_order_total_freight` - Shipping cost
- `first_order_payment_type` - Payment method
- `first_order_payment_installments` - Installment count

**Target Variable**: `IS_REPEAT` - 1 if the customer made a second purchase, 0 otherwise.

---

## 📁 Project Structure

```
olist_ml_pipeline/
├── README.md # This file
├── requirements.txt # Python dependencies
├── config/
│ └── config.yaml # Configuration (optional)
├── src/
│ ├── init.py
│ ├── pipeline.py # Main orchestrator
│ ├── etl/
│ │ ├── init.py
│ │ └── incremental_load.py # Day 5: Incremental ETL
│ ├── features/
│ │ ├── init.py
│ │ └── first_order_features.py # Day 9: Feature engineering
│ └── model/
│ ├── init.py
│ ├── train_model.py # Day 10: Model training
│ └── predict.py # Day 11: UDF deployment & scoring
├── sql/
│ ├── 01_create_features_table.sql # Creates customer_features_with_label
│ ├── 02_daily_sales_summary.sql # Daily sales dashboard
│ └── 03_monitoring.sql # Monitoring queries
└── notebooks/
└── exploration.ipynb # Data exploration (optional)
```


---

## 🚀 Prerequisites

### Snowflake Requirements
- A Snowflake account with **ACCOUNTADMIN** privileges (or sufficient permissions)
- Database: `ALIM_DB`
- Schema: `ALIM_SCHEMA`
- Warehouse: `COMPUTE_WH` (or your preferred warehouse)

### Olist Dataset
The Olist dataset must be loaded into your Snowflake schema. It should include these tables:
- `olist_customers`
- `olist_orders`
- `olist_order_items`
- `olist_order_payments`
- `olist_order_reviews`
- `olist_products`
- `olist_sellers`

### Python Dependencies
```bash
pip install -r requirements.txt

## 🔧 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/olist_ml_pipeline.git
cd olist_ml_pipeline
```

### 2. Set Up Snowflake Git Integration

Run this SQL in a Snowflake worksheet:

```sql
-- Create API integration
CREATE OR REPLACE API INTEGRATION github_olist_api
    API_PROVIDER = git_https_api
    API_ALLOWED_PREFIXES = ('https://github.com/yourusername/')
    API_USER_AUTHENTICATION = (TYPE = SNOWFLAKE_GITHUB_APP)
    ENABLED = TRUE;

-- Create Git repository
CREATE OR REPLACE GIT REPOSITORY olist_ml_repo
    API_INTEGRATION = github_olist_api
    ORIGIN = 'https://github.com/yourusername/olist_ml_pipeline.git';

-- Sync with GitHub
ALTER GIT REPOSITORY olist_ml_repo FETCH;
```

> **Important**: Complete the GitHub OAuth flow when prompted by Snowsight.

### 3. Create Required Tables

Run this SQL to create the feature table:

```sql
-- Execute the SQL from the repository
EXECUTE IMMEDIATE FROM @olist_ml_repo/branches/main/sql/01_create_features_table.sql;
```

### 4. Run the Pipeline

In a Snowflake Python worksheet:

```python
import sys

# Add the src directory from GitHub
sys.path.append('@olist_ml_repo/branches/main/src')

from pipeline import run_full_pipeline

# Get session
from snowflake.snowpark.context import get_active_session
session = get_active_session()

# Run the pipeline
run_full_pipeline(session)
```

---

## 🏃 How It Works

### The Pipeline Steps

```python
def run_full_pipeline(session):
    # Step 1: Incremental ETL (Day 5)
    new_orders = run_incremental_load(session)
    
    # Step 2: Feature Engineering (Day 9)
    create_first_order_features(session)
    
    # Step 3: Model Training (Day 10)
    model, features, accuracy = train_model(session)
    
    # Step 4: Deploy UDF (Day 11)
    deploy_udf(session, model, features)
    
    # Step 5: Score All Customers (Day 11)
    score_customers(session, features)
    
    # Step 6: Dashboard Updates
    update_daily_sales_summary(session)
```

---

## ⭐ Key Features

### 1. Incremental ETL

- Loads only **new orders** (not full refresh)
- Tracks last load timestamp in `etl_control` table
- Efficient and cost-effective

### 2. First-Order Features

- **Prevents data leakage** by using only first-order data
- Simulates real-world prediction scenario
- Features include delivery time, spend, payment method

### 3. Model Training & Evaluation

- Random Forest Classifier
- Accuracy: ~70-75% (depending on data)
- Feature importance analysis included

### 4. UDF Deployment

- Model deployed as Snowflake Python UDF
- Real-time scoring capability
- No data movement required

### 5. Customer Segmentation

| Segment | Repeat Probability |
|---------|-------------------|
| High | >= 70% |
| Medium | 40-70% |
| Low | < 40% |

### 6. Production Monitoring

- Stream on `silver_orders` for change tracking
- Task runs every 5 minutes
- Alert triggers on >10 cancellations in 24 hours

---

## 📊 Usage

### Run the Full Pipeline

```python
from pipeline import run_full_pipeline
run_full_pipeline(session)
```

### Score a Single Customer

```sql
SELECT 
    customer_unique_id,
    predict_repeat(
        first_order_delivery_days,
        first_order_items_count,
        first_order_total_spend,
        first_order_avg_item_price,
        first_order_total_freight,
        first_order_payment_installments
    ) AS repeat_score
FROM customer_features_with_label
WHERE customer_unique_id = 'abc123';
```

### Query Predictions

```sql
-- View customer segmentation
SELECT 
    CASE 
        WHEN repeat_score >= 0.7 THEN 'High'
        WHEN repeat_score >= 0.4 THEN 'Medium'
        ELSE 'Low'
    END AS segment,
    COUNT(*) AS customers
FROM customer_repeat_scores
GROUP BY segment;
```

---

## 📈 Monitoring

### Task History

```sql
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE TASK_NAME = 'PROCESS_NEW_ORDERS'
ORDER BY SCHEDULED_TIME DESC;
```

### Stream Status

```sql
SELECT SYSTEM$STREAM_GET_TABLE_TIMESTAMP(
    'ALIM_DB.ALIM_SCHEMA.SILVER_ORDERS_STREAM'
);
```

### Alert History

```sql
SELECT *
FROM TABLE(INFORMATION_SCHEMA.ALERT_HISTORY())
WHERE ALERT_NAME = 'HIGH_CANCELLATION_ALERT'
ORDER BY SCHEDULED_TIME DESC;
```

### Check Predictions

```sql
-- Distribution of repeat scores
SELECT 
    ROUND(repeat_score, 2) AS score_bucket,
    COUNT(*) AS customers
FROM customer_repeat_scores
GROUP BY score_bucket
ORDER BY score_bucket;
```

---

## 🔄 CI/CD with Git

### Development Workflow

**1. Create a feature branch**

```bash
git checkout -b feature/new-feature
```

**2. Make changes in your local workspace**

**3. Commit and push**

```bash
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

**4. Create a pull request on GitHub**

**5. Merge to main after review**

**6. Deploy in Snowflake**

```sql
ALTER GIT REPOSITORY olist_ml_repo FETCH;
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/pipeline.py` | Main orchestrator - runs all steps |
| `src/etl/incremental_load.py` | Day 5 - Incremental ETL |
| `src/features/first_order_features.py` | Day 9 - Feature engineering |
| `src/model/train_model.py` | Day 10 - Model training |
| `src/model/predict.py` | Day 11 - UDF deployment & scoring |
| `sql/01_create_features_table.sql` | Creates feature table with IS_REPEAT label |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is for educational purposes. The Olist dataset is provided by Olist under a CC BY-NC-SA 4.0 license.
