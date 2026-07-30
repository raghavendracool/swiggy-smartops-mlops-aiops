import json
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==================================================
# 1. Project Paths and API URLs
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "swiggy_delay_model_small.pkl"
FEATURES_PATH = BASE_DIR / "models" / "model_features.pkl"
ANOMALY_PATH = BASE_DIR / "reports" / "anomaly_report.csv"
METRICS_PATH = BASE_DIR / "reports" / "model_metrics.json"

# FastAPI backend URL
BACKEND_BASE_URL = "http://127.0.0.1:8000"
LIVE_ORDERS_API = f"{BACKEND_BASE_URL}/admin/orders"


# ==================================================
# 2. Streamlit Page Config
# ==================================================

st.set_page_config(
    page_title="Swiggy SmartOps",
    page_icon="🍔",
    layout="wide"
)


# ==================================================
# 3. Load Model and Local Files
# ==================================================

@st.cache_resource
def load_model_files():
    model = joblib.load(MODEL_PATH)
    model_features = joblib.load(FEATURES_PATH)
    return model, model_features


def load_metrics():
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r") as file:
            return json.load(file)
    return None


def load_anomaly_report():
    if ANOMALY_PATH.exists():
        return pd.read_csv(ANOMALY_PATH)
    return None


def load_live_app_orders():
    """
    This function connects Streamlit dashboard to FastAPI backend.

    React app places orders -> FastAPI stores orders + ML prediction
    This dashboard calls /admin/orders and displays those live orders.
    """
    try:
        response = requests.get(LIVE_ORDERS_API, timeout=10)

        if response.status_code == 200:
            return pd.DataFrame(response.json())

        st.error(f"Backend API error: {response.status_code}")
        return None

    except Exception as e:
        st.error("Unable to connect to FastAPI backend.")
        st.warning("Make sure backend is running on http://127.0.0.1:8000")
        st.exception(e)
        return None


# ==================================================
# 4. Batch Prediction Helper Code
# ==================================================

RAW_MODEL_FEATURES = [
    "city",
    "device_type",
    "gross_amount",
    "coupon_discount_amount",
    "membership_benefit_amount",
    "total_discount_amount",
    "net_amount",
    "quantity",
    "rating",
    "order_month",
    "order_dayofweek",
    "coupon_used_num",
    "surge_num",
    "raining_num",
    "campaign_exposed_num",
    "delivery_success_num",
    "membership_tier",
    "restaurant_name",
    "product_name",
    "cuisine_tag",
    "coupon_name",
    "campaign_name",
    "channel",
    "objective"
]


DEFAULT_VALUES = {
    "city": "Hyderabad",
    "device_type": "Android",
    "gross_amount": 800.0,
    "coupon_discount_amount": 0.0,
    "membership_benefit_amount": 0.0,
    "total_discount_amount": 0.0,
    "quantity": 1,
    "rating": 4.0,
    "coupon_used_num": 0,
    "surge_num": 0,
    "raining_num": 0,
    "campaign_exposed_num": 0,
    "delivery_success_num": 1,
    "membership_tier": "NONE",
    "restaurant_name": "Demo Restaurant",
    "product_name": "Demo Product",
    "cuisine_tag": "Biryani",
    "coupon_name": "NONE",
    "campaign_name": "NONE",
    "channel": "NONE",
    "objective": "NONE"
}


def convert_flag(value):
    value = str(value).strip().lower()

    if value in ["1", "yes", "true", "y"]:
        return 1

    if value in ["0", "no", "false", "n"]:
        return 0

    return 0


def score_new_orders(new_orders_df):
    df = new_orders_df.copy()

    for col, default_value in DEFAULT_VALUES.items():
        if col not in df.columns:
            df[col] = default_value

    numeric_cols = [
        "gross_amount",
        "coupon_discount_amount",
        "membership_benefit_amount",
        "total_discount_amount",
        "quantity",
        "rating"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(DEFAULT_VALUES[col])

    flag_cols = [
        "coupon_used_num",
        "surge_num",
        "raining_num",
        "campaign_exposed_num",
        "delivery_success_num"
    ]

    for col in flag_cols:
        df[col] = df[col].apply(convert_flag)

    if "net_amount" not in df.columns:
        df["net_amount"] = df["gross_amount"] - df["total_discount_amount"]
    else:
        df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce")
        df["net_amount"] = df["net_amount"].fillna(
            df["gross_amount"] - df["total_discount_amount"]
        )

    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        df["order_month"] = df["transaction_date"].dt.month.fillna(7).astype(int)
        df["order_dayofweek"] = df["transaction_date"].dt.dayofweek.fillna(2).astype(int)
    else:
        df["order_month"] = 7
        df["order_dayofweek"] = 2

    model_input = df[RAW_MODEL_FEATURES].copy()

    encoded_input = pd.get_dummies(model_input)
    encoded_input = encoded_input.reindex(columns=model_features, fill_value=0)

    predictions = model.predict(encoded_input)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(encoded_input)[:, 1]
    else:
        probabilities = [0.0] * len(predictions)

    df["delay_prediction"] = predictions
    df["delay_risk"] = df["delay_prediction"].apply(
        lambda x: "High Delay Risk" if x == 1 else "Low Delay Risk"
    )
    df["delay_probability"] = probabilities

    df["recommendation"] = df["delay_prediction"].apply(
        lambda x: "Increase delivery partner availability / monitor zone"
        if x == 1
        else "Normal monitoring"
    )

    return df


# ==================================================
# 5. Load ML Model
# ==================================================

try:
    model, model_features = load_model_files()
except Exception as e:
    st.error("Model files not loaded. Please check models folder.")
    st.exception(e)
    st.stop()


# ==================================================
# 6. Main App Header
# ==================================================

st.title("🍔 Swiggy SmartOps")
st.caption("MLOps + AIOps Delivery Delay Prediction Application")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Home",
        "Delay Prediction",
        "Batch Prediction",
        "Live App Orders",
        "AIOps Monitoring",
        "Model Info"
    ]
)


# ==================================================
# 7. Home Page
# ==================================================

if page == "Home":
    st.header("Project Overview")

    st.success("Application loaded successfully.")

    st.write("""
    **Swiggy SmartOps** is an interview-ready **MLOps + AIOps project**.

    This application has two parts:

    1. **Customer-facing fullstack app**  
       React frontend + FastAPI backend + database + ML prediction.

    2. **MLOps/Admin dashboard**  
       Streamlit dashboard to monitor batch predictions, live orders, AIOps metrics, and model information.
    """)

    st.subheader("Current Architecture")

    st.code("""
React Frontend
  ↓
FastAPI Backend
  ↓
SQLite DB now / AWS RDS later
  ↓
ML Model Prediction
  ↓
Order + Prediction Stored
  ↓
Streamlit MLOps Dashboard Reads Backend API
    """)

    st.subheader("Business Use Case")

    st.write("""
    When a user places an order in the mini Swiggy app, the backend saves the order
    and immediately calls the trained ML model to predict delay risk.

    The Streamlit dashboard can then read those live orders from the backend API
    and show high-risk orders, low-risk orders, and operational insights.
    """)


# ==================================================
# 8. Single Delay Prediction Page
# ==================================================

elif page == "Delay Prediction":
    st.header("Delivery Delay Prediction")

    st.write("Enter order details below and click **Predict Delay Risk**.")

    col1, col2, col3 = st.columns(3)

    with col1:
        city = st.selectbox("City", ["Hyderabad", "Bangalore"])
        device_type = st.selectbox("Device Type", ["Android", "iOS", "Web"])
        gross_amount = st.number_input("Gross Amount", min_value=0.0, value=800.0, step=50.0)
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)

    with col2:
        coupon_discount_amount = st.number_input(
            "Coupon Discount Amount",
            min_value=0.0,
            value=50.0,
            step=10.0
        )

        membership_benefit_amount = st.number_input(
            "Membership Benefit Amount",
            min_value=0.0,
            value=20.0,
            step=10.0
        )

        total_discount_amount = st.number_input(
            "Total Discount Amount",
            min_value=0.0,
            value=80.0,
            step=10.0
        )

        net_amount = gross_amount - total_discount_amount

        rating = st.slider(
            "Rating",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )

    with col3:
        coupon_used_num = st.selectbox(
            "Coupon Used",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        surge_num = st.selectbox(
            "Surge Active",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        raining_num = st.selectbox(
            "Raining",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        campaign_exposed_num = st.selectbox(
            "Campaign Exposed",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        delivery_success_num = st.selectbox(
            "Delivery Success",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        membership_tier = st.selectbox(
            "Membership Tier",
            ["NONE", "ONE_LITE", "ONE", "ONE_PLUS"]
        )

    st.subheader("Product, Coupon and Campaign Details")

    col4, col5, col6 = st.columns(3)

    with col4:
        cuisine_tag = st.selectbox(
            "Cuisine",
            ["Biryani", "Pizza", "Chinese", "South Indian", "North Indian", "Burger", "Desserts"]
        )

        restaurant_name = st.text_input("Restaurant Name", "Demo Restaurant")

    with col5:
        product_name = st.text_input("Product Name", "Demo Product")

        coupon_name = st.selectbox(
            "Coupon Name",
            ["NONE", "WELCOME50", "WEEKEND20", "PAYDAY15", "SAVE80", "FREESHIP"]
        )

    with col6:
        campaign_name = st.selectbox(
            "Campaign Name",
            ["NONE", "Campaign A", "Campaign B", "Campaign C"]
        )

        channel = st.selectbox(
            "Campaign Channel",
            ["NONE", "Push", "Email", "SMS", "Social"]
        )

        objective = st.selectbox(
            "Campaign Objective",
            ["NONE", "Acquisition", "Retention", "Conversion"]
        )

    st.info(f"Calculated Net Amount: {net_amount}")

    input_df = pd.DataFrame([{
        "city": city,
        "device_type": device_type,
        "gross_amount": gross_amount,
        "coupon_discount_amount": coupon_discount_amount,
        "membership_benefit_amount": membership_benefit_amount,
        "total_discount_amount": total_discount_amount,
        "net_amount": net_amount,
        "quantity": quantity,
        "rating": rating,
        "order_month": 7,
        "order_dayofweek": 2,
        "coupon_used_num": coupon_used_num,
        "surge_num": surge_num,
        "raining_num": raining_num,
        "campaign_exposed_num": campaign_exposed_num,
        "delivery_success_num": delivery_success_num,
        "membership_tier": membership_tier,
        "restaurant_name": restaurant_name,
        "product_name": product_name,
        "cuisine_tag": cuisine_tag,
        "coupon_name": coupon_name,
        "campaign_name": campaign_name,
        "channel": channel,
        "objective": objective
    }])

    input_encoded = pd.get_dummies(input_df)
    input_encoded = input_encoded.reindex(columns=model_features, fill_value=0)

    if st.button("Predict Delay Risk"):
        prediction = model.predict(input_encoded)[0]

        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(input_encoded)[0][1]
        else:
            probability = 0.0

        st.subheader("Prediction Result")

        if prediction == 1:
            st.error(f"High Delay Risk | Probability: {probability:.2f}")
        else:
            st.success(f"Low Delay Risk | Probability: {probability:.2f}")

        st.subheader("Business Reasoning")

        reasons = []

        if raining_num == 1:
            reasons.append("Rain is active, which can increase delivery time.")
        if surge_num == 1:
            reasons.append("Surge is active, which indicates high demand.")
        if coupon_used_num == 1:
            reasons.append("Coupon is used, useful for revenue and promotion monitoring.")
        if gross_amount > 1000:
            reasons.append("High-value order may need priority handling.")
        if rating < 3:
            reasons.append("Low rating input indicates customer experience risk.")
        if campaign_exposed_num == 1:
            reasons.append("Campaign exposed order may have different customer behavior.")

        if not reasons:
            reasons.append("No major operational risk indicators selected.")

        for reason in reasons:
            st.write("- " + reason)

        st.subheader("Recommendation")

        if prediction == 1:
            st.warning("""
            Recommended Action:
            - Increase delivery partner availability
            - Monitor city-level delay trend
            - Check rain and surge impact
            - Prioritize high-value or customer-sensitive orders
            """)
        else:
            st.success("""
            Recommended Action:
            - Order looks operationally stable
            - Continue normal monitoring
            """)


# ==================================================
# 9. Batch Prediction Page
# ==================================================

elif page == "Batch Prediction":
    st.header("Batch Prediction - New Orders")

    st.write("""
    Upload a CSV file containing new order records.
    The app will score each order and predict whether it has high delivery delay risk.
    """)

    st.subheader("Download Sample Input CSV")

    sample_orders = pd.DataFrame([
        {
            "order_id": "NEW1001",
            "transaction_date": "2026-07-28",
            "city": "Hyderabad",
            "device_type": "Android",
            "gross_amount": 1200,
            "coupon_discount_amount": 100,
            "membership_benefit_amount": 50,
            "total_discount_amount": 150,
            "quantity": 2,
            "rating": 4.2,
            "coupon_used_num": 1,
            "surge_num": 1,
            "raining_num": 1,
            "campaign_exposed_num": 1,
            "delivery_success_num": 1,
            "membership_tier": "ONE_PLUS",
            "restaurant_name": "Demo Restaurant",
            "product_name": "Paneer Biryani",
            "cuisine_tag": "Biryani",
            "coupon_name": "WELCOME50",
            "campaign_name": "Campaign A",
            "channel": "Push",
            "objective": "Retention"
        },
        {
            "order_id": "NEW1002",
            "transaction_date": "2026-07-28",
            "city": "Bangalore",
            "device_type": "iOS",
            "gross_amount": 450,
            "coupon_discount_amount": 0,
            "membership_benefit_amount": 0,
            "total_discount_amount": 0,
            "quantity": 1,
            "rating": 4.8,
            "coupon_used_num": 0,
            "surge_num": 0,
            "raining_num": 0,
            "campaign_exposed_num": 0,
            "delivery_success_num": 1,
            "membership_tier": "NONE",
            "restaurant_name": "Demo Restaurant",
            "product_name": "Burger",
            "cuisine_tag": "Burger",
            "coupon_name": "NONE",
            "campaign_name": "NONE",
            "channel": "NONE",
            "objective": "NONE"
        }
    ])

    sample_csv = sample_orders.to_csv(index=False)

    st.download_button(
        label="Download new_orders_sample.csv",
        data=sample_csv,
        file_name="new_orders_sample.csv",
        mime="text/csv"
    )

    st.subheader("Upload New Orders CSV")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:
        new_orders_df = pd.read_csv(uploaded_file)

        st.write("Uploaded data preview:")
        st.dataframe(new_orders_df.head())

        if st.button("Score New Orders"):
            scored_orders = score_new_orders(new_orders_df)

            st.success("Batch prediction completed successfully.")

            st.subheader("Scored Orders")
            st.dataframe(scored_orders)

            high_risk_count = (scored_orders["delay_prediction"] == 1).sum()
            low_risk_count = (scored_orders["delay_prediction"] == 0).sum()

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Orders Scored", len(scored_orders))
            col2.metric("High Delay Risk Orders", int(high_risk_count))
            col3.metric("Low Delay Risk Orders", int(low_risk_count))

            output_path = BASE_DIR / "reports" / "scored_orders.csv"
            scored_orders.to_csv(output_path, index=False)

            scored_csv = scored_orders.to_csv(index=False)

            st.download_button(
                label="Download scored_orders.csv",
                data=scored_csv,
                file_name="scored_orders.csv",
                mime="text/csv"
            )

            st.info(f"Scored output also saved locally at: {output_path}")


# ==================================================
# 10. Live App Orders Page
# ==================================================

elif page == "Live App Orders":
    st.header("Live Orders from Fullstack App")

    st.write("""
    This page automatically reads orders created from the React frontend application.
    The data comes from the FastAPI backend `/admin/orders` endpoint.
    """)

    st.info(f"Reading live orders from: {LIVE_ORDERS_API}")

    live_orders_df = load_live_app_orders()

    if live_orders_df is not None and not live_orders_df.empty:
        st.subheader("Latest Orders and ML Predictions")
        st.dataframe(live_orders_df)

        total_orders = len(live_orders_df)

        high_risk_orders = (
            live_orders_df["delay_risk"] == "High Delay Risk"
        ).sum()

        low_risk_orders = (
            live_orders_df["delay_risk"] == "Low Delay Risk"
        ).sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total App Orders", int(total_orders))
        col2.metric("High Delay Risk", int(high_risk_orders))
        col3.metric("Low Delay Risk", int(low_risk_orders))

        if "city" in live_orders_df.columns:
            st.subheader("Orders by City")

            city_orders = (
                live_orders_df.groupby("city")
                .size()
                .reset_index(name="orders")
            )

            fig_city = px.bar(
                city_orders,
                x="city",
                y="orders",
                title="Orders by City"
            )

            st.plotly_chart(fig_city, use_container_width=True)

        if "delay_risk" in live_orders_df.columns:
            st.subheader("Delay Risk Distribution")

            risk_count = (
                live_orders_df.groupby("delay_risk")
                .size()
                .reset_index(name="orders")
            )

            fig_risk = px.pie(
                risk_count,
                names="delay_risk",
                values="orders",
                title="Delay Risk Distribution"
            )

            st.plotly_chart(fig_risk, use_container_width=True)

        st.subheader("High Risk Orders")

        high_risk_df = live_orders_df[
            live_orders_df["delay_risk"] == "High Delay Risk"
        ]

        st.dataframe(high_risk_df)

    else:
        st.warning("No live orders found. Place an order from the React app first.")


# ==================================================
# 11. AIOps Monitoring Page
# ==================================================

elif page == "AIOps Monitoring":
    st.header("AIOps Monitoring Dashboard")

    anomaly_df = load_anomaly_report()

    if anomaly_df is None:
        st.warning("anomaly_report.csv not found inside reports folder.")
    else:
        st.subheader("Latest Operational Metrics")
        st.dataframe(anomaly_df.tail(20))

        col1, col2, col3 = st.columns(3)

        revenue_anomalies = int(anomaly_df["revenue_anomaly"].sum())
        delay_anomalies = int(anomaly_df["delivery_delay_anomaly"].sum())
        order_anomalies = int(anomaly_df["orders_anomaly"].sum())

        col1.metric("Revenue Anomalies", revenue_anomalies)
        col2.metric("Delivery Delay Anomalies", delay_anomalies)
        col3.metric("Order Count Anomalies", order_anomalies)

        st.subheader("Daily Revenue Trend")

        fig1 = px.line(
            anomaly_df,
            x="transaction_date",
            y="total_revenue",
            title="Daily Revenue Trend"
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Average Delivery Minutes Trend")

        fig2 = px.line(
            anomaly_df,
            x="transaction_date",
            y="avg_delivery_minutes",
            title="Average Delivery Minutes Trend"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Daily Orders Trend")

        fig3 = px.line(
            anomaly_df,
            x="transaction_date",
            y="total_orders",
            title="Daily Orders Trend"
        )

        st.plotly_chart(fig3, use_container_width=True)


# ==================================================
# 12. Model Info Page
# ==================================================

elif page == "Model Info":
    st.header("Model Information")

    metrics = load_metrics()

    if metrics is None:
        st.warning("model_metrics.json not found inside reports folder.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Accuracy", metrics.get("accuracy"))
        col2.metric("Precision", metrics.get("precision"))
        col3.metric("Recall", metrics.get("recall"))
        col4.metric("F1 Score", metrics.get("f1_score"))

        st.subheader("Full Model Metrics")
        st.json(metrics)

    st.subheader("Model Artifacts")

    st.write("Model file:", str(MODEL_PATH))
    st.write("Feature file:", str(FEATURES_PATH))
    st.write("Total encoded features:", len(model_features))

    st.subheader("Model Features")

    st.dataframe(
        pd.DataFrame({
            "feature_name": model_features
        })
    )