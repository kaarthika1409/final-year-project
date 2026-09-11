"""
Diet Recommendation Model Training Script
==========================================
Run this script ONCE to train and save the best model:

    python ml_models/train_model.py

The backend will NOT retrain on startup - it simply loads:
    backend/ml_models/diet_model.pkl
"""

import sys
import os

# Force UTF-8 output on Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

import importlib.util
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

warnings.filterwarnings("ignore")

# ------------------------------------
# Resolve paths relative to this file
# ------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)

TRAIN_CSV = os.path.join(BACKEND_DIR, "data", "processed_patient_train.csv")
TEST_CSV = os.path.join(BACKEND_DIR, "data", "processed_patient_test.csv")
CLEAN_CSV = os.path.join(BACKEND_DIR, "data", "clean_patient_dataset.csv")
LABEL_ENCODER_PATH = os.path.join(BACKEND_DIR, "data", "diet_label_encoder.pkl")
MODEL_OUT = os.path.join(BACKEND_DIR, "ml_models", "diet_model.pkl")
METADATA_OUT = os.path.join(BACKEND_DIR, "ml_models", "model_metadata.pkl")
PREPROCESSOR_PY = os.path.join(SCRIPT_DIR, "diet_preprocessor.py")


def _load_dp_module():
    """Dynamically load diet_preprocessor.py."""
    spec = importlib.util.spec_from_file_location("diet_preprocessor", PREPROCESSOR_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fit_preprocessor():
    """Fit and save the preprocessing pipeline on the clean patient dataset."""
    print("\n" + "=" * 60)
    print("FITTING PATIENT PREPROCESSOR")
    print("=" * 60)
    dp = _load_dp_module()
    pp = dp.fit_and_save_preprocessor(force=True)
    print("  Preprocessor fitted and saved.")
    # Verify output feature count
    import pandas as pd_inner
    df = pd_inner.read_csv(CLEAN_CSV)
    X_sample = df[dp.NUMERIC_COLS + dp.CATEGORICAL_COLS].head(1)
    out_shape = pp.transform(X_sample).shape
    print(f"  Output feature dimensions: {out_shape[1]}")
    return dp, pp, out_shape[1]


def load_data_from_clean_csv(dp_module, preprocessor):
    """Load clean_patient_dataset.csv, preprocess with the fitted pipeline."""
    print("\n" + "=" * 60)
    print("LOADING & PREPROCESSING CLEAN PATIENT DATA")
    print("=" * 60)

    df = pd.read_csv(CLEAN_CSV)
    print(f"Clean CSV   : {CLEAN_CSV}")
    print(f"Raw shape   : {df.shape}")

    TARGET = "Diet_Recommendation"
    X_raw = df[dp_module.NUMERIC_COLS + dp_module.CATEGORICAL_COLS].copy()
    y_raw = df[TARGET].values

    # Encode labels
    le = joblib.load(LABEL_ENCODER_PATH)
    y_enc = le.transform(y_raw)

    X = preprocessor.transform(X_raw)

    # Stratified split: 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    feature_cols = [str(i) for i in range(X.shape[1])]
    class_names = list(le.classes_)

    print(f"Total samples    : {len(X)}")
    print(f"Training samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")
    print(f"Features         : {X.shape[1]}")
    print(f"Diet classes     : {class_names}")
    print(f"Target distribution (train):")
    unique, counts = np.unique(y_train, return_counts=True)
    for u, c in zip(unique, counts):
        print(f"  class {u} ({class_names[u]}): {c} samples")

    return X_train, y_train, X_test, y_test, feature_cols, class_names, le


def evaluate_model(model, X_test, y_test, class_names, model_name):
    """Evaluate a trained model and return metrics dict."""
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n{'-'*50}")
    print(f"  {model_name}")
    print(f"{'-'*50}")
    print(f"  Accuracy  : {acc:.4f}")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(f"  F1 Score  : {f1:.4f}")
    print(f"\nClassification Report:\n{report}")
    print(f"Confusion Matrix:\n{cm}")

    return {
        "model_name": model_name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "classification_report": report,
        "confusion_matrix": cm,
    }


def train_all_models(X_train, y_train):
    """Train all three classifiers and return them."""
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=42, solver="lbfgs"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.1, max_depth=4, random_state=42
        ),
    }

    trained = {}
    print("\n" + "=" * 60)
    print("TRAINING MODELS")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n  Training: {name} ...")
        model.fit(X_train, y_train)
        trained[name] = model
        print(f"  Done: {name}")

    return trained


def select_best(results):
    """Select best model by F1-score (tie-break: accuracy)."""
    sorted_results = sorted(
        results.values(),
        key=lambda r: (r["f1_score"], r["accuracy"]),
        reverse=True,
    )
    return sorted_results[0]


def print_comparison_table(results):
    """Print a formatted comparison table."""
    print("\n" + "=" * 60)
    print("MODEL COMPARISON TABLE")
    print("=" * 60)
    header = f"{'Model':<30} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1 Score':>10}"
    print(header)
    print("-" * 75)
    for r in results.values():
        row = (
            f"{r['model_name']:<30} "
            f"{r['accuracy']:>10.4f} "
            f"{r['precision']:>10.4f} "
            f"{r['recall']:>10.4f} "
            f"{r['f1_score']:>10.4f}"
        )
        print(row)
    print("-" * 75)


def save_artifacts(best_model_obj, best_result, feature_cols, class_names):
    """Save the best model and metadata."""
    print("\n" + "=" * 60)
    print("SAVING MODEL ARTIFACTS")
    print("=" * 60)

    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)

    joblib.dump(best_model_obj, MODEL_OUT)
    print(f"  Saved model     : {MODEL_OUT}")

    metadata = {
        "model_name": best_result["model_name"],
        "feature_names": feature_cols,
        "target_classes": class_names,
        "num_features": len(feature_cols),
        "num_classes": len(class_names),
        "evaluation_metrics": {
            "accuracy": best_result["accuracy"],
            "precision": best_result["precision"],
            "recall": best_result["recall"],
            "f1_score": best_result["f1_score"],
        },
        "classification_report": best_result["classification_report"],
        "confusion_matrix": best_result["confusion_matrix"].tolist(),
    }
    joblib.dump(metadata, METADATA_OUT)
    print(f"  Saved metadata  : {METADATA_OUT}")


def run_sample_prediction(best_model_obj, le, X_test, y_test):
    """Run a sample prediction on one test record and print results."""
    print("\n" + "=" * 60)
    print("SAMPLE PREDICTION TEST")
    print("=" * 60)

    idx = 0
    sample = X_test[idx].reshape(1, -1)
    actual_encoded = int(y_test[idx])
    actual_name = le.inverse_transform([actual_encoded])[0]

    pred_encoded = int(best_model_obj.predict(sample)[0])
    pred_name = le.inverse_transform([pred_encoded])[0]

    confidence = None
    if hasattr(best_model_obj, "predict_proba"):
        proba = best_model_obj.predict_proba(sample)[0]
        confidence = round(float(np.max(proba)), 4)

    print(f"  Actual Diet         : {actual_name}  (encoded: {actual_encoded})")
    print(f"  Predicted Diet      : {pred_name}  (encoded: {pred_encoded})")
    if confidence is not None:
        print(f"  Prediction Confidence: {confidence:.4f} ({confidence*100:.1f}%)")
    else:
        print("  Prediction Confidence: N/A (model does not support predict_proba)")


def main():
    print("\n" + "=" * 60)
    print("  DIET RECOMMENDATION MODEL TRAINING")
    print("=" * 60)

    # 1. Fit and save the patient preprocessor (compatible with current sklearn)
    dp_module, preprocessor, n_features = fit_preprocessor()

    # 2. Load clean patient data and preprocess
    X_train, y_train, X_test, y_test, feature_cols, class_names, le = load_data_from_clean_csv(
        dp_module, preprocessor
    )

    # 3. Train all models
    trained_models = train_all_models(X_train, y_train)

    # 4. Evaluate all models
    print("\n" + "=" * 60)
    print("EVALUATING MODELS ON TEST SET")
    print("=" * 60)

    results = {}
    for name, model in trained_models.items():
        results[name] = evaluate_model(model, X_test, y_test, class_names, name)

    # 5. Comparison table
    print_comparison_table(results)

    # 6. Select best model
    best_result = select_best(results)
    best_model_name = best_result["model_name"]
    best_model_obj = trained_models[best_model_name]

    print("\n" + "=" * 60)
    print("BEST MODEL SELECTED")
    print("=" * 60)
    print(f"  Best Model    : {best_result['model_name']}")
    print(f"  Best Accuracy : {best_result['accuracy']:.4f}")
    print(f"  Best Precision: {best_result['precision']:.4f}")
    print(f"  Best Recall   : {best_result['recall']:.4f}")
    print(f"  Best F1 Score : {best_result['f1_score']:.4f}")

    # 7. Save model + metadata
    save_artifacts(best_model_obj, best_result, feature_cols, class_names)

    # 8. Sample prediction
    run_sample_prediction(best_model_obj, le, X_test, y_test)

    # 9. Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  Dataset shape (total)       : ({len(X_train) + len(X_test)}, {n_features + 1})")
    print(f"  Training samples            : {len(X_train)}")
    print(f"  Testing samples             : {len(X_test)}")
    print(f"  Number of features          : {n_features}")
    print(f"  Number of diet classes      : {len(class_names)}")
    print(f"  Class names                 : {class_names}")
    print(f"  Best model                  : {best_result['model_name']}")
    print(f"  Accuracy                    : {best_result['accuracy']:.4f}")
    print(f"  Precision                   : {best_result['precision']:.4f}")
    print(f"  Recall                      : {best_result['recall']:.4f}")
    print(f"  F1 Score                    : {best_result['f1_score']:.4f}")
    print(f"  Saved model location        : {MODEL_OUT}")
    print(f"  Saved metadata location     : {METADATA_OUT}")
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
