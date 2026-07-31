from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DATABASE_URL = "sqlite:///./swiggy_orders.db"

DATA_DIR = ROOT_DIR / "data" / "enriched"

MODEL_PATH = ROOT_DIR / "models" / "swiggy_delay_model_v2_location_weather.pkl"
FEATURES_PATH = ROOT_DIR / "models" / "model_input_features_v2.pkl"

MODEL_VERSION = "v2_location_weather"

BACKEND_TITLE = "Swiggy SmartOps Fullstack API"
BACKEND_VERSION = "4.0.0"