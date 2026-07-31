from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DATABASE_URL = "sqlite:///./swiggy_orders.db"

DATA_DIR = ROOT_DIR / "data" / "enriched"
REPORTS_DIR = ROOT_DIR / "reports"

MODEL_PATH = ROOT_DIR / "models" / "swiggy_delay_model_v2_location_weather.pkl"
FEATURES_PATH = ROOT_DIR / "models" / "model_input_features_v2.pkl"

CUSTOMER_CHURN_MODEL_PATH = ROOT_DIR / "models" / "swiggy_customer_churn_model_v1.pkl"
CUSTOMER_CHURN_FEATURES_PATH = ROOT_DIR / "models" / "customer_churn_features_v1.pkl"

MODEL_VERSION = "v2_location_weather"

BACKEND_TITLE = "Swiggy SmartOps Fullstack API"
BACKEND_VERSION = "5.0.0"