"""
Demographic Accuracy Evaluation Report Script
---------------------------------------------
Compares predicted daily calorie targets vs actual intake logs across test users
grouped by Age, Gender, and BMI category. Outputs MAE and RMSE per group.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.evaluation import evaluate_demographic_accuracy


def run_evaluation_report():
    print("=" * 80)
    print("      DEMOGRAPHIC ACCURACY EVALUATION REPORT (CALORIE PREDICTION ENGINE)")
    print("=" * 80)

    report = evaluate_demographic_accuracy()

    print(f"Total Evaluated Test Samples : {report.total_users}")
    print(f"Overall MAE (Mean Absolute Error)  : {report.overall_mae:.2f} kcal")
    print(f"Overall RMSE (Root Mean Sq Error)  : {report.overall_rmse:.2f} kcal")
    print("-" * 80)

    print(f"{'Group Type':<15} | {'Demographic Group':<18} | {'Count':<6} | {'MAE (kcal)':<10} | {'RMSE (kcal)':<10}")
    print("-" * 80)

    for item in report.group_metrics:
        print(
            f"{item.group_type:<15} | {item.group_name:<18} | {item.sample_count:<6} | {item.mae:<10.2f} | {item.rmse:<10.2f}"
        )

    print("=" * 80)
    print("Evaluation completed successfully.")


if __name__ == "__main__":
    run_evaluation_report()
