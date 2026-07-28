# Swiggy SmartOps - MLOps and AIOps Project

## Project Overview

Swiggy SmartOps is an interview-ready MLOps and AIOps project built using Databricks, Python, Scikit-learn, Streamlit, GitHub, and AWS.

The project predicts delivery delay risk using Swiggy-style food delivery transaction data and provides an AIOps monitoring dashboard for revenue, order, and delivery-time anomalies.

## Tech Stack

- Databricks
- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- Plotly
- Joblib
- GitHub
- AWS EC2

## Architecture

```text
Databricks
  ↓
Data Cleaning + Feature Engineering
  ↓
RandomForest ML Model Training
  ↓
Model Files + Metrics + Anomaly Report
  ↓
Streamlit Application
  ↓
AWS EC2 Deployment