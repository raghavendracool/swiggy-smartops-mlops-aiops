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
REPORTS_DIR = BASE_DIR / "reports"

# MLOps business report files generated from Databricks Notebook 05
MLOPS_SUMMARY_PATH = REPORTS_DIR / "mlops_business_summary.json"
CUSTOMER_RETENTION_PATH = REPORTS_DIR / "customer_retention_risk.csv"
COUPON_RECOMMENDATIONS_PATH = REPORTS_DIR / "coupon_recommendations.csv"
RESTAURANT_RISK_PATH = REPORTS_DIR / "restaurant_ops_risk.csv"
AREA_RISK_PATH = REPORTS_DIR / "area_ops_risk.csv"
CHURN_METRICS_PATH = REPORTS_DIR / "customer_churn_metrics_v1.json"

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
# 3.1 MLOps Business Dashboard Helper Functions
# ==================================================

def load_csv_report(file_name):
    file_path = REPORTS_DIR / file_name

    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path)


def load_json_report(file_name):
    file_path = REPORTS_DIR / file_name

    if not file_path.exists():
        return {}

    with open(file_path, "r") as file:
        return json.load(file)


def safe_number(value, default=0):
    try:
        if pd.isna(value):
            return default
        return value
    except Exception:
        return default


def format_rupees(value):
    try:
        return f"₹{float(value):,.0f}"
    except Exception:
        return "₹0"


def inject_dashboard_css():
    st.markdown(
        """
        <style>
        .mlops-hero {
            background: linear-gradient(135deg, #fc8019 0%, #ffb84d 100%);
            padding: 28px 32px;
            border-radius: 24px;
            color: white;
            margin-bottom: 24px;
            box-shadow: 0 12px 28px rgba(252, 128, 25, 0.22);
        }
        .mlops-hero h1 {
            margin: 0;
            font-size: 36px;
            font-weight: 900;
        }
        .mlops-hero p {
            margin-top: 8px;
            font-size: 16px;
            opacity: 0.95;
        }
        .kpi-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 20px;
            border-left: 6px solid #fc8019;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            min-height: 128px;
        }
        .kpi-card-danger {
            border-left-color: #dc2626;
            background: #fff7f7;
        }
        .kpi-label {
            color: #686b78;
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .kpi-value {
            color: #171a29;
            font-size: 30px;
            font-weight: 900;
            margin-top: 8px;
        }
        .kpi-caption {
            color: #686b78;
            font-size: 13px;
            margin-top: 8px;
            line-height: 1.4;
        }
        .insight-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            border: 1px solid #f0f0f0;
            margin-bottom: 16px;
        }
        .insight-card h3 {
            margin-top: 0;
            color: #171a29;
        }
        .business-note {
            background: #fff7ed;
            border-left: 6px solid #fc8019;
            padding: 16px 18px;
            border-radius: 14px;
            margin: 14px 0;
        }
        .file-ok {
            color: #166534;
            font-weight: 800;
        }
        .file-missing {
            color: #991b1b;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, caption="", danger=False):
    cls = "kpi-card kpi-card-danger" if danger else "kpi-card"
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_report_file_status():
    st.subheader("Report File Status")

    files = [
        ("mlops_business_summary.json", MLOPS_SUMMARY_PATH),
        ("customer_retention_risk.csv", CUSTOMER_RETENTION_PATH),
        ("coupon_recommendations.csv", COUPON_RECOMMENDATIONS_PATH),
        ("restaurant_ops_risk.csv", RESTAURANT_RISK_PATH),
        ("area_ops_risk.csv", AREA_RISK_PATH),
        ("customer_churn_metrics_v1.json", CHURN_METRICS_PATH),
    ]

    status_rows = []

    for file_name, path in files:
        status_rows.append(
            {
                "file_name": file_name,
                "expected_path": str(path),
                "status": "Available" if path.exists() else "Missing",
            }
        )

    st.dataframe(pd.DataFrame(status_rows), use_container_width=True)


def display_existing_columns(df, preferred_columns, max_rows=50):
    if df.empty:
        st.warning("No data available for this section.")
        return

    columns = [col for col in preferred_columns if col in df.columns]

    if not columns:
        st.dataframe(df.head(max_rows), use_container_width=True)
    else:
        st.dataframe(df[columns].head(max_rows), use_container_width=True)


def render_mlops_business_dashboard():
    inject_dashboard_css()

    st.markdown(
        """
        <div class="mlops-hero">
            <h1>📊 Swiggy SmartOps MLOps Business Dashboard</h1>
            <p>Customer retention, smart coupons, restaurant operations, area risk, live order risk and business impact monitoring.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary = load_json_report("mlops_business_summary.json")
    churn_metrics = load_json_report("customer_churn_metrics_v1.json")
    customer_retention = load_csv_report("customer_retention_risk.csv")
    coupon_recommendations = load_csv_report("coupon_recommendations.csv")
    restaurant_risk = load_csv_report("restaurant_ops_risk.csv")
    area_risk = load_csv_report("area_ops_risk.csv")
    live_orders_df = load_live_app_orders()

    if not summary:
        st.error("MLOps summary file is missing. Put mlops_business_summary.json inside the reports folder.")
        show_report_file_status()
        return

    live_total_orders = 0
    live_high_risk = 0
    live_revenue_at_risk = 0
    live_avg_probability = 0

    if live_orders_df is not None and not live_orders_df.empty:
        live_total_orders = len(live_orders_df)

        if "delay_risk" in live_orders_df.columns:
            live_high_risk = int((live_orders_df["delay_risk"] == "High Delay Risk").sum())

        if "net_amount" in live_orders_df.columns and "delay_risk" in live_orders_df.columns:
            live_revenue_at_risk = live_orders_df.loc[
                live_orders_df["delay_risk"] == "High Delay Risk",
                "net_amount"
            ].fillna(0).sum()

        if "delay_probability" in live_orders_df.columns:
            live_avg_probability = live_orders_df["delay_probability"].fillna(0).mean()

    st.subheader("Executive Business Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            "Total Customers",
            f"{summary.get('total_customers', 0):,}",
            "Customers analyzed from monthly order behavior",
        )

    with col2:
        kpi_card(
            "High Churn Customers",
            f"{summary.get('high_churn_customers', 0):,}",
            "Customers with major order drop",
            danger=True,
        )

    with col3:
        kpi_card(
            "Coupon Candidates",
            f"{summary.get('customers_needing_coupon', 0):,}",
            "Customers recommended for campaign/coupon",
        )

    with col4:
        kpi_card(
            "Revenue at Risk",
            format_rupees(summary.get("total_revenue_at_risk", 0)),
            "Previous revenue from churn-risk customers",
            danger=True,
        )

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        kpi_card(
            "Live App Orders",
            f"{live_total_orders:,}",
            "Orders placed from React app and scored by FastAPI",
        )

    with col6:
        kpi_card(
            "Live High Risk Orders",
            f"{live_high_risk:,}",
            "Live orders currently predicted as high delay risk",
            danger=live_high_risk > 0,
        )

    with col7:
        kpi_card(
            "Live Revenue at Risk",
            format_rupees(live_revenue_at_risk),
            "Live order revenue exposed to delay risk",
            danger=live_revenue_at_risk > 0,
        )

    with col8:
        kpi_card(
            "Avg Live Risk Prob",
            f"{live_avg_probability:.2f}",
            "Average live model probability from backend",
        )

    st.markdown(
        f"""
        <div class="business-note">
        <b>Business message:</b> This dashboard connects ML outputs to Swiggy decisions. It helps reduce delivery delays, detect customer order drop, recommend coupons, monitor risky restaurants, and plan area operations.<br>
        <b>Analysis Window:</b> Previous Month = {summary.get('previous_month', '-')}, Latest Month = {summary.get('latest_month', '-')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Live Orders",
            "Customer Retention",
            "Coupon Engine",
            "Restaurant Ops",
            "Area Ops",
            "Model/MLOps Story",
        ]
    )

    with tab1:
        st.subheader("Live Orders from React + FastAPI")

        if live_orders_df is None or live_orders_df.empty:
            st.warning("No live orders found. Place an order from React app first.")
        else:
            c1, c2 = st.columns(2)

            with c1:
                if "delay_risk" in live_orders_df.columns:
                    risk_count = live_orders_df["delay_risk"].value_counts().reset_index()
                    risk_count.columns = ["delay_risk", "orders"]
                    fig = px.pie(
                        risk_count,
                        names="delay_risk",
                        values="orders",
                        title="Live Delay Risk Distribution",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                scenario_col = "business_scenario" if "business_scenario" in live_orders_df.columns else "operational_scenario"
                if scenario_col in live_orders_df.columns:
                    scenario_count = live_orders_df[scenario_col].value_counts().head(10).reset_index()
                    scenario_count.columns = ["scenario", "orders"]
                    fig = px.bar(
                        scenario_count,
                        x="scenario",
                        y="orders",
                        title="Live Business Scenarios",
                    )
                    fig.update_layout(xaxis_tickangle=-30)
                    st.plotly_chart(fig, use_container_width=True)

            display_existing_columns(
                live_orders_df,
                [
                    "order_id",
                    "user_id",
                    "receiver_name",
                    "receiver_type",
                    "customer_area",
                    "restaurant_area",
                    "distance_km",
                    "estimated_travel_minutes",
                    "weather_condition",
                    "delay_risk",
                    "delay_probability",
                    "priority_level",
                    "business_scenario",
                    "business_action",
                    "business_impact",
                    "recommendation",
                ],
                max_rows=100,
            )

    with tab2:
        st.subheader("Customer Order Drop / Churn Risk")

        if customer_retention.empty:
            st.warning("customer_retention_risk.csv not found in reports folder.")
        else:
            risk_filter_options = ["All"]
            if "churn_risk_label" in customer_retention.columns:
                risk_filter_options += sorted(customer_retention["churn_risk_label"].dropna().unique().tolist())

            risk_filter = st.selectbox("Filter by churn risk", risk_filter_options)

            filtered = customer_retention.copy()
            if risk_filter != "All" and "churn_risk_label" in filtered.columns:
                filtered = filtered[filtered["churn_risk_label"] == risk_filter]

            c1, c2 = st.columns(2)

            with c1:
                if "churn_risk_label" in customer_retention.columns:
                    risk_count = customer_retention["churn_risk_label"].value_counts().reset_index()
                    risk_count.columns = ["churn_risk_label", "customers"]
                    fig = px.bar(
                        risk_count,
                        x="churn_risk_label",
                        y="customers",
                        title="Customers by Churn Risk",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                if "customer_segment" in customer_retention.columns:
                    segment_count = customer_retention["customer_segment"].value_counts().head(8).reset_index()
                    segment_count.columns = ["customer_segment", "customers"]
                    fig = px.pie(
                        segment_count,
                        names="customer_segment",
                        values="customers",
                        title="Customer Segments",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if "revenue_at_risk" in filtered.columns:
                filtered = filtered.sort_values("revenue_at_risk", ascending=False)

            display_existing_columns(
                filtered,
                [
                    "customer_id",
                    "city",
                    "customer_area",
                    "membership_tier",
                    "customer_segment",
                    "previous_monthly_orders",
                    "current_monthly_orders",
                    "order_drop_count",
                    "order_drop_pct",
                    "previous_monthly_revenue",
                    "current_monthly_revenue",
                    "revenue_drop_pct",
                    "churn_risk_label",
                    "revenue_at_risk",
                ],
                max_rows=100,
            )

    with tab3:
        st.subheader("Smart Coupon Recommendation Engine")

        if coupon_recommendations.empty:
            st.warning("coupon_recommendations.csv not found in reports folder.")
        else:
            c1, c2 = st.columns(2)

            with c1:
                if "recommended_coupon" in coupon_recommendations.columns:
                    coupon_count = coupon_recommendations["recommended_coupon"].value_counts().reset_index()
                    coupon_count.columns = ["recommended_coupon", "customers"]
                    fig = px.bar(
                        coupon_count,
                        x="recommended_coupon",
                        y="customers",
                        title="Recommended Coupons",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                if "customer_segment" in coupon_recommendations.columns:
                    coupon_segment = coupon_recommendations.groupby("customer_segment").size().reset_index(name="customers")
                    fig = px.bar(
                        coupon_segment,
                        x="customer_segment",
                        y="customers",
                        title="Coupon Candidates by Segment",
                    )
                    fig.update_layout(xaxis_tickangle=-30)
                    st.plotly_chart(fig, use_container_width=True)

            if "revenue_at_risk" in coupon_recommendations.columns:
                coupon_recommendations = coupon_recommendations.sort_values("revenue_at_risk", ascending=False)

            display_existing_columns(
                coupon_recommendations,
                [
                    "customer_id",
                    "city",
                    "customer_area",
                    "customer_segment",
                    "previous_monthly_orders",
                    "current_monthly_orders",
                    "churn_risk_label",
                    "recommended_coupon",
                    "coupon_reason",
                    "business_action",
                    "revenue_at_risk",
                ],
                max_rows=100,
            )

    with tab4:
        st.subheader("Restaurant Operations Risk")

        if restaurant_risk.empty:
            st.warning("restaurant_ops_risk.csv not found in reports folder.")
        else:
            restaurant_name_col = "restaurant_location_name"
            if restaurant_name_col not in restaurant_risk.columns:
                restaurant_name_col = "assigned_nearby_restaurant_name"

            if "delay_rate_pct" in restaurant_risk.columns:
                top_restaurants = restaurant_risk.sort_values("delay_rate_pct", ascending=False).head(20)
            else:
                top_restaurants = restaurant_risk.head(20)

            if restaurant_name_col in top_restaurants.columns and "delay_rate_pct" in top_restaurants.columns:
                fig = px.bar(
                    top_restaurants,
                    x=restaurant_name_col,
                    y="delay_rate_pct",
                    color="restaurant_priority" if "restaurant_priority" in top_restaurants.columns else None,
                    title="Top Restaurants by Delay Rate",
                )
                fig.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig, use_container_width=True)

            display_existing_columns(
                top_restaurants,
                [
                    "restaurant_id",
                    restaurant_name_col,
                    "restaurant_area",
                    "total_orders",
                    "total_revenue",
                    "delay_rate_pct",
                    "rain_order_pct",
                    "avg_delivery_minutes",
                    "avg_distance_km",
                    "avg_rating",
                    "restaurant_priority",
                    "business_action",
                ],
                max_rows=50,
            )

    with tab5:
        st.subheader("Area Operations Risk")

        if area_risk.empty:
            st.warning("area_ops_risk.csv not found in reports folder.")
        else:
            if "delay_rate_pct" in area_risk.columns:
                top_areas = area_risk.sort_values("delay_rate_pct", ascending=False).head(20)
            else:
                top_areas = area_risk.head(20)

            if "customer_area" in top_areas.columns and "delay_rate_pct" in top_areas.columns:
                fig = px.bar(
                    top_areas,
                    x="customer_area",
                    y="delay_rate_pct",
                    color="area_priority" if "area_priority" in top_areas.columns else None,
                    title="Area-wise Delay Risk",
                )
                fig.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig, use_container_width=True)

            display_existing_columns(
                top_areas,
                [
                    "city_clean",
                    "customer_area",
                    "total_orders",
                    "total_revenue",
                    "delay_rate_pct",
                    "rain_order_pct",
                    "avg_delivery_minutes",
                    "avg_distance_km",
                    "avg_rating",
                    "area_priority",
                    "business_action",
                ],
                max_rows=50,
            )

    with tab6:
        st.subheader("MLOps + Business Story")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                """
### What Swiggy gains

- Detect high delay-risk orders before customer complaint.
- Identify customers whose order frequency is dropping.
- Recommend coupons only where business value exists.
- Monitor restaurants causing delay risk.
- Monitor areas needing more delivery partners.
- Track revenue at risk from churn and delay.
                """
            )

        with col_b:
            st.markdown(
                """
### What an MLOps engineer does here

- Builds Databricks feature-engineering pipelines.
- Trains and versions ML models.
- Saves model artifacts and business reports.
- Deploys model through FastAPI.
- Monitors live predictions and business KPIs.
- Plans retraining when data drift or business drift appears.
                """
            )

        st.subheader("Customer Churn Model Metrics")
        if churn_metrics:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", churn_metrics.get("accuracy", "-"))
            c2.metric("Precision", churn_metrics.get("precision", "-"))
            c3.metric("Recall", churn_metrics.get("recall", "-"))
            c4.metric("F1", churn_metrics.get("f1_score", "-"))
            st.json(churn_metrics)
        else:
            st.info("customer_churn_metrics_v1.json not found. Add it to reports folder after training churn model.")

        show_report_file_status()


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
st.caption("MLOps + AIOps + Customer Retention + Smart Coupon Intelligence")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Home",
        "Delay Prediction",
        "Batch Prediction",
        "Live App Orders",
        "AIOps Monitoring",
        "MLOps Business Dashboard",
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
# 12. MLOps Business Dashboard Page
# ==================================================

elif page == "MLOps Business Dashboard":
    render_mlops_business_dashboard()


# ==================================================
# 13. Model Info Page
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