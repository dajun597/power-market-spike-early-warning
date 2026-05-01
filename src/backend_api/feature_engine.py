from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class FeatureConfigError(Exception):
    """Raised when the feature config is invalid."""


class InputValidationError(Exception):
    """Raised when API input data is invalid."""


class ConfigDrivenFeatureEngine:
    """
    Config-driven feature engine.

    The important backend idea:
    The code is generic. The domain-specific columns and feature rules live in JSON config.
    """

    def __init__(self, config_path: str | Path = "src/backend_api/config/feature_config.json") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config(self.config_path)

    def _load_config(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FeatureConfigError(f"Feature config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        required_keys = [
            "time_column",
            "raw_required_columns",
            "numeric_columns",
            "lag_features",
            "derived_features",
            "model_feature_columns",
        ]
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise FeatureConfigError(f"Missing config keys: {missing}")

        return config

    def _validate_input_columns(self, df: pd.DataFrame) -> None:
        required_columns = self.config["raw_required_columns"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise InputValidationError(f"Missing required input columns: {missing}")

    def _parse_time_column(self, df: pd.DataFrame) -> pd.DataFrame:
        time_col = self.config["time_column"]
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

        if df[time_col].isna().any():
            raise InputValidationError(
                f"Invalid values in time column '{time_col}'. "
                "Use ISO format, for example 2025-01-01T00:00:00."
            )

        return df.sort_values(time_col).reset_index(drop=True)

    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_columns = self.config["numeric_columns"]

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        bad_cols = [col for col in numeric_columns if df[col].isna().any()]
        if bad_cols:
            raise InputValidationError(f"Invalid or missing numeric values in columns: {bad_cols}")

        return df

    def _create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        for item in self.config["lag_features"]:
            source = item["source"]
            lag = int(item.get("lag", 1))
            output = item["output"]

            if source not in df.columns:
                raise FeatureConfigError(f"Lag source column not found: {source}")

            df[output] = df[source].shift(lag)

        return df

    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        for item in self.config["derived_features"]:
            name = item["name"]
            operation = item["operation"]

            if operation == "divide":
                numerator = item["numerator"]
                denominator = item["denominator"]

                self._ensure_columns_exist(df, [numerator, denominator])
                df[name] = df[numerator] / df[denominator].replace(0, np.nan)

            elif operation == "multiply":
                left = item["left"]
                right = item["right"]

                self._ensure_columns_exist(df, [left, right])
                df[name] = df[left] * df[right]

            elif operation == "add":
                left = item["left"]
                right = item["right"]

                self._ensure_columns_exist(df, [left, right])
                df[name] = df[left] + df[right]

            elif operation == "subtract":
                left = item["left"]
                right = item["right"]

                self._ensure_columns_exist(df, [left, right])
                df[name] = df[left] - df[right]

            else:
                raise FeatureConfigError(f"Unsupported derived feature operation: {operation}")

        return df

    def _ensure_columns_exist(self, df: pd.DataFrame, columns: list[str]) -> None:
        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise FeatureConfigError(f"Columns required by feature rule are missing: {missing}")

    def build_features(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        if raw_df.empty:
            raise InputValidationError("Input records are empty.")

        df = raw_df.copy()

        self._validate_input_columns(df)
        df = self._parse_time_column(df)
        df = self._convert_numeric_columns(df)
        df = self._create_lag_features(df)
        df = self._create_derived_features(df)

        df = df.replace([np.inf, -np.inf], np.nan)

        model_features = self.config["model_feature_columns"]
        self._ensure_columns_exist(df, model_features)

        feature_df = df.dropna(subset=model_features).copy()

        if feature_df.empty:
            raise InputValidationError(
                "No valid rows after feature engineering. "
                "Lag features require previous records, so send at least two ordered records."
            )

        return feature_df[model_features]
