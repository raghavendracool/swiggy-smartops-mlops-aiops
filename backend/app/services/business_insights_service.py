import json

import numpy as np
import pandas as pd

from backend.app.config import REPORTS_DIR


def clean_records(df: pd.DataFrame):
    df = df.replace({np.nan: None})
    return df.to_dict(orient="records")


def read_csv_report(file_name: str, limit: int | None = None):
    file_path = REPORTS_DIR / file_name

    if not file_path.exists():
        return []

    df = pd.read_csv(file_path)

    if limit is not None:
        df = df.head(limit)

    return clean_records(df)


def read_json_report(file_name: str):
    file_path = REPORTS_DIR / file_name

    if not file_path.exists():
        return {}

    with open(file_path, "r") as file:
        return json.load(file)


def get_customer_retention_records(limit=100, risk="All"):
    file_path = REPORTS_DIR / "customer_retention_risk.csv"

    if not file_path.exists():
        return []

    df = pd.read_csv(file_path)

    if risk != "All" and "churn_risk_label" in df.columns:
        df = df[df["churn_risk_label"] == risk]

    sort_cols = []
    ascending = []

    if "churn_risk_label" in df.columns:
        sort_cols.append("churn_risk_label")
        ascending.append(True)

    if "revenue_at_risk" in df.columns:
        sort_cols.append("revenue_at_risk")
        ascending.append(False)

    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=ascending)

    return clean_records(df.head(limit))


def get_coupon_recommendation_records(limit=100):
    file_path = REPORTS_DIR / "coupon_recommendations.csv"

    if not file_path.exists():
        return []

    df = pd.read_csv(file_path)

    if "revenue_at_risk" in df.columns:
        df = df.sort_values("revenue_at_risk", ascending=False)

    return clean_records(df.head(limit))


def get_restaurant_risk_records(limit=100):
    file_path = REPORTS_DIR / "restaurant_ops_risk.csv"

    if not file_path.exists():
        return []

    df = pd.read_csv(file_path)

    if "delay_rate_pct" in df.columns:
        df = df.sort_values("delay_rate_pct", ascending=False)

    return clean_records(df.head(limit))


def get_area_risk_records(limit=100):
    file_path = REPORTS_DIR / "area_ops_risk.csv"

    if not file_path.exists():
        return []

    df = pd.read_csv(file_path)

    if "delay_rate_pct" in df.columns:
        df = df.sort_values("delay_rate_pct", ascending=False)

    return clean_records(df.head(limit))


def get_mlops_business_summary():
    return read_json_report("mlops_business_summary.json")