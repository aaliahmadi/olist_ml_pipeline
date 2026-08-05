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
```
│ ├── 02_daily_sales_summary.sql # Daily sales dashboard
│ └── 03_monitoring.sql # Monitoring queries
└── notebooks/
└── exploration.ipynb # Data exploration (optional)
