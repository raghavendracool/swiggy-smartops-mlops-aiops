import json
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# 1. Project Paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "swiggy_delay_model_small.pkl"
FEATURES_PATH = BASE_DIR / "models" / "model_features.pkl"
ANOMALY_PATH = BASE_DIR / "reports" / "anomaly_report.csv"
METRICS_PATH = BASE_DIR / "reports" / "model_metrics.json"


# ==================================================
# 2. Streamlit Page Config
# ==================================================

st.set_page_config(
    page_title="Swiggy SmartOps",
    page_icon="🍔",
    layout="wide"
)


# ==================================================
# 3. Load Model and Files
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


try:
    model, model_features = load_model_files()
except Exception as e:
    st.error("Model files not loaded. Please check models folder.")
    st.exception(e)
    st.stop()


# ==================================================
# 4. Main App Header
# ==================================================

st.title("🍔 Swiggy SmartOps")
st.caption("MLOps + AIOps Delivery Delay Prediction Application")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Home",
        "Delay Prediction",
        "AIOps Monitoring",
        "Model Info"
    ]
)


# ==================================================
# 5. Home Page
# ==================================================

if page == "Home":
    st.header("Project Overview")

    st.success("Application loaded successfully.")

    st.write("""
    **Swiggy SmartOps** is an interview-ready **MLOps + AIOps project**.

    This application predicts delivery delay risk using Swiggy-style food delivery
    transaction data. The machine learning model was trained in Databricks and
    the final application is built using Streamlit.
    """)

    st.subheader("Architecture")

    st.code("""
Databricks
  ↓
Data Loading from Swiggy Tables
  ↓
Data Cleaning + Feature Engineering
  ↓
RandomForest ML Model Training
  ↓
Model Files + Feature List + Metrics + Anomaly Report
  ↓
Streamlit Application
  ↓
GitHub + AWS EC2 Deployment
    """)

    st.subheader("Business Use Case")

    st.write("""
    Food delivery operations teams need to identify orders that may get delayed.
    This app allows a user to enter order details such as city, rain, surge,
    coupon, campaign, membership, cuisine, and order value. The model then predicts
    whether the order has a high delay risk.
    """)

    st.subheader("Project Deliverables")

    st.write("""
    - Delivery delay prediction model
    - Business reasoning for prediction output
    - AIOps anomaly monitoring dashboard
    - Model metrics page
    - Streamlit application for interview demo
    - Ready for AWS EC2 deployment
    """)


# ==================================================
# 6. Delay Prediction Page
# ==================================================

elif page == "Delay Prediction":
    st.header("Delivery Delay Prediction")

    st.write("Enter order details below and click **Predict Delay Risk**.")

    col1, col2, col3 = st.columns(3)

    with col1:
        city = st.selectbox(
            "City",
            ["Hyderabad", "Bangalore"]
        )

        device_type = st.selectbox(
            "Device Type",
            ["Android", "iOS", "Web"]
        )

        gross_amount = st.number_input(
            "Gross Amount",
            min_value=0.0,
            value=800.0,
            step=50.0
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1
        )

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
            [
                "Biryani",
                "Pizza",
                "Chinese",
                "South Indian",
                "North Indian",
                "Burger",
                "Desserts"
            ]
        )

        restaurant_name = st.text_input(
            "Restaurant Name",
            "Demo Restaurant"
        )

    with col5:
        product_name = st.text_input(
            "Product Name",
            "Demo Product"
        )

        coupon_name = st.selectbox(
            "Coupon Name",
            [
                "NONE",
                "WELCOME50",
                "WEEKEND20",
                "PAYDAY15",
                "SAVE80",
                "FREESHIP"
            ]
        )

    with col6:
        campaign_name = st.selectbox(
            "Campaign Name",
            [
                "NONE",
                "Campaign A",
                "Campaign B",
                "Campaign C"
            ]
        )

        channel = st.selectbox(
            "Campaign Channel",
            [
                "NONE",
                "Push",
                "Email",
                "SMS",
                "Social"
            ]
        )

        objective = st.selectbox(
            "Campaign Objective",
            [
                "NONE",
                "Acquisition",
                "Retention",
                "Conversion"
            ]
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

    input_encoded = input_encoded.reindex(
        columns=model_features,
        fill_value=0
    )

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

        with st.expander("Show Encoded Model Input"):
            st.dataframe(input_encoded)


# ==================================================
# 7. AIOps Monitoring Page
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
# 8. Model Info Page
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