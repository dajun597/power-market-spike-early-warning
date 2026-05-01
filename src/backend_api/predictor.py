from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


class SpikePredictor:
    """
    Prediction wrapper.

    Loads the model once and exposes a simple predict method.
    """

    def __init__(
        self,
        model_path: str | Path = "models_storage/lgb_model.pkl",
        config_path: str | Path = "models_storage/config.json",
    ) -> None:
        self.model_path = Path(model_path)
        self.config_path = Path(config_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}. "
                "Put lgb_model.pkl in models_storage/."
            )

        self.model = joblib.load(self.model_path)

        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                model_config = json.load(f)
        else:
            model_config = {}

        self.threshold = float(model_config.get("threshold", 0.2))

    def risk_level(self, probability: float) -> str:
        if probability >= 0.3:
            return "HIGH"
        if probability >= 0.2:
            return "MEDIUM"
        if probability >= 0.1:
            return "MODERATE"
        return "LOW"

    def predict(self, feature_df: pd.DataFrame) -> list[dict]:
        probabilities = self.model.predict_proba(feature_df)[:, 1]
        predictions = (probabilities >= self.threshold).astype(int)

        return [
            {
                "row_index": int(feature_df.index[i]),
                "spike_probability": round(float(prob), 6),
                "is_spike_predicted": int(predictions[i]),
                "risk_level": self.risk_level(float(prob)),
                "threshold": self.threshold,
            }
            for i, prob in enumerate(probabilities)
        ]
