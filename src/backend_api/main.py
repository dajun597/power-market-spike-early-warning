from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.backend_api.feature_engine import (
    ConfigDrivenFeatureEngine,
    FeatureConfigError,
    InputValidationError,
)
from src.backend_api.predictor import SpikePredictor


app = FastAPI(
    title="Config-Driven UK Power Market Spike Prediction API",
    description=(
        "A backend API wrapper that uses JSON configuration for input schema "
        "and feature engineering rules."
    ),
    version="0.2.0",
)


class BatchPredictionRequest(BaseModel):
    # This intentionally uses dicts instead of fixed Pydantic fields.
    # The real schema is controlled by feature_config.json.
    records: list[dict[str, Any]] = Field(
        ...,
        description="Raw power-market records. Required fields are defined in src/backend_api/config/feature_config.json.",
    )


try:
    feature_engine = ConfigDrivenFeatureEngine()
    predictor = SpikePredictor()
    startup_error = None
except Exception as exc:
    feature_engine = None
    predictor = None
    startup_error = str(exc)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok" if startup_error is None else "degraded",
        "feature_engine_loaded": feature_engine is not None,
        "model_loaded": predictor is not None,
        "startup_error": startup_error,
    }


@app.get("/schema")
def get_expected_schema() -> dict:
    """
    Return the current expected input schema and feature rules.

    This endpoint is useful because the API is config-driven.
    Users can check what fields the service expects.
    """
    if feature_engine is None:
        raise HTTPException(status_code=500, detail=f"Feature engine failed to load: {startup_error}")

    return feature_engine.config


@app.post("/predict/batch")
def predict_batch(request: BatchPredictionRequest) -> dict:
    if startup_error is not None:
        raise HTTPException(status_code=500, detail=f"API startup failed: {startup_error}")

    try:
        raw_df = pd.DataFrame(request.records)
        feature_df = feature_engine.build_features(raw_df)
        results = predictor.predict(feature_df)

        return {
            "status": "success",
            "input_rows": len(raw_df),
            "feature_rows": len(feature_df),
            "prediction_rows": len(results),
            "results": results,
        }

    except InputValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except FeatureConfigError as exc:
        raise HTTPException(status_code=500, detail=f"Feature configuration error: {exc}")

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during prediction.")
