"""
diet_preprocessor.py
====================
Fits a ColumnTransformer on clean_patient_dataset.csv using the CURRENT
installed scikit-learn version, so it can actually be loaded at prediction
time (the original patient_preprocessor.pkl was created with sklearn 1.6.1
and cannot be deserialized under sklearn 1.9+).

Run once (automatically called from train_model.py):
    python ml_models/train_model.py

Or manually:
    python -c "from backend.ml_models.diet_preprocessor import fit_and_save_preprocessor; fit_and_save_preprocessor()"
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# ---------------------------------------------------------------
# Column definitions matching clean_patient_dataset.csv
# ---------------------------------------------------------------
NUMERIC_COLS = [
    "Age",
    "Weight_kg",
    "Height_cm",
    "BMI",
    "Daily_Caloric_Intake",
    "Cholesterol_mg/dL",
    "Blood_Pressure_mmHg",
    "Glucose_mg/dL",
    "Weekly_Exercise_Hours",
    "Adherence_to_Diet_Plan",
    "Dietary_Nutrient_Imbalance_Score",
]

CATEGORICAL_COLS = [
    "Gender",
    "Disease_Type",
    "Severity",
    "Physical_Activity_Level",
    "Dietary_Restrictions",
    "Allergies",
    "Preferred_Cuisine",
]

# Known categories observed in the dataset
CATEGORY_VALUES = {
    "Gender":                  ["Female", "Male"],
    "Disease_Type":            ["Diabetes", "Hypertension", "Obesity"],
    "Severity":                ["Mild", "Moderate", "Severe"],
    "Physical_Activity_Level": ["Active", "Moderate", "Sedentary"],
    "Dietary_Restrictions":    ["Low_Sodium", "Low_Sugar"],
    "Allergies":               ["Gluten", "Peanuts"],
    "Preferred_Cuisine":       ["Chinese", "Indian", "Italian", "Mexican"],
}

# Paths
_SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR  = os.path.dirname(_SCRIPT_DIR)
_CLEAN_CSV    = os.path.join(_BACKEND_DIR, "data", "clean_patient_dataset.csv")
_PREPROCESSOR_OUT = os.path.join(_SCRIPT_DIR, "diet_preprocessor.pkl")


def _build_pipeline() -> ColumnTransformer:
    """Build the ColumnTransformer with StandardScaler + OHE."""
    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])

    categorical_transformer = Pipeline(steps=[
        (
            "ohe",
            OneHotEncoder(
                categories=[CATEGORY_VALUES[c] for c in CATEGORICAL_COLS],
                handle_unknown="ignore",
                sparse_output=False,
            ),
        )
    ])

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_COLS),
            ("cat", categorical_transformer, CATEGORICAL_COLS),
        ],
        remainder="drop",
    )


def fit_and_save_preprocessor(force: bool = False) -> ColumnTransformer:
    """
    Fits the ColumnTransformer on clean_patient_dataset.csv and saves it.
    Returns the fitted preprocessor.
    """
    if os.path.exists(_PREPROCESSOR_OUT) and not force:
        return joblib.load(_PREPROCESSOR_OUT)

    if not os.path.exists(_CLEAN_CSV):
        raise FileNotFoundError(f"Clean patient CSV not found: {_CLEAN_CSV}")

    df = pd.read_csv(_CLEAN_CSV)
    X = df[NUMERIC_COLS + CATEGORICAL_COLS].copy()

    ct = _build_pipeline()
    ct.fit(X)

    joblib.dump(ct, _PREPROCESSOR_OUT)
    print(f"[diet_preprocessor] Saved preprocessor -> {_PREPROCESSOR_OUT}")
    print(f"[diet_preprocessor] Output features: {ct.transform(X[:1]).shape[1]}")
    return ct


# ---------------------------------------------------------------
# Module-level cached preprocessor (lazy load)
# ---------------------------------------------------------------
_cached_preprocessor: ColumnTransformer = None


def get_preprocessor() -> ColumnTransformer:
    """Returns the fitted preprocessor, loading from disk if needed."""
    global _cached_preprocessor
    if _cached_preprocessor is None:
        if not os.path.exists(_PREPROCESSOR_OUT):
            raise FileNotFoundError(
                f"diet_preprocessor.pkl not found at '{_PREPROCESSOR_OUT}'. "
                "Run: python ml_models/train_model.py"
            )
        _cached_preprocessor = joblib.load(_PREPROCESSOR_OUT)
    return _cached_preprocessor


def preprocess_patient(raw_input: dict) -> np.ndarray:
    """
    Transforms a raw patient dict into the 33-feature numpy array
    expected by diet_model.pkl.

    Parameters
    ----------
    raw_input : dict
        Keys must include all NUMERIC_COLS and CATEGORICAL_COLS.

    Returns
    -------
    np.ndarray of shape (1, 33)
    """
    pp = get_preprocessor()
    df = pd.DataFrame([raw_input])

    # Ensure correct column types
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return pp.transform(df[NUMERIC_COLS + CATEGORICAL_COLS])
