import joblib
import pandas as pd

from backend.app.config import FEATURES_PATH, MODEL_PATH, MODEL_VERSION

model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)


def predict_delay(ml_input: dict):
    input_df = pd.DataFrame([ml_input])

    input_df = input_df.reindex(
        columns=model_features,
        fill_value=None
    )

    prediction = int(model.predict(input_df)[0])

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(input_df)[0][1])
    else:
        probability = 0.0

    delay_risk = "High Delay Risk" if prediction == 1 else "Low Delay Risk"

    recommendation = (
        "Increase delivery partner availability / monitor zone"
        if prediction == 1
        else "Normal monitoring"
    )

    return {
        "model_version": MODEL_VERSION,
        "delay_prediction": prediction,
        "delay_probability": probability,
        "delay_risk": delay_risk,
        "recommendation": recommendation,
    }