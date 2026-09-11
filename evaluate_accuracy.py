"""
Accuracy Evaluation & Results Generator (Stage 6)
--------------------------------------------------
Runs accuracy evaluation on test demographic samples, computes MAE, RMSE, and MAPE,
and outputs formatted CSV table (accuracy_results.csv) and bar chart (accuracy_chart.png).
"""

import sys
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.app.evaluation import evaluate_demographic_accuracy


def run_accuracy_evaluation(csv_output: str = "accuracy_results.csv", chart_output: str = "accuracy_chart.png"):
    print("=" * 85)
    print("      DEMOGRAPHIC ACCURACY EVALUATION REPORT (CALORIE PREDICTION ENGINE)")
    print("=" * 85)

    report = evaluate_demographic_accuracy()

    print(f"Total Evaluated Test Samples : {report.total_users}")
    print(f"Overall MAE (Mean Absolute Error)     : {report.overall_mae:.2f} kcal")
    print(f"Overall RMSE (Root Mean Sq Error)     : {report.overall_rmse:.2f} kcal")
    print(f"Overall MAPE (Mean Abs % Error)       : {report.overall_mape:.2f} %")
    print("-" * 85)

    print(f"{'Group Type':<15} | {'Demographic Group':<18} | {'Count':<6} | {'MAE (kcal)':<10} | {'RMSE (kcal)':<10} | {'MAPE (%)':<9}")
    print("-" * 85)

    # 1. Export CSV
    with open(csv_output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Group Type", "Demographic Group", "Sample Count", "MAE (kcal)", "RMSE (kcal)", "MAPE (%)", "Avg Actual (kcal)", "Avg Predicted (kcal)"])

        for item in report.group_metrics:
            print(
                f"{item.group_type:<15} | {item.group_name:<18} | {item.sample_count:<6} | {item.mae:<10.2f} | {item.rmse:<10.2f} | {item.mape:<9.2f}"
            )
            writer.writerow([
                item.group_type,
                item.group_name,
                item.sample_count,
                item.mae,
                item.rmse,
                item.mape,
                item.avg_actual,
                item.avg_predicted,
            ])

    print("-" * 85)
    print(f"[Results Export] Saved table results CSV to {csv_output}")

    # 2. Generate Bar Chart Visualization
    try:
        groups = [f"{item.group_type}\n({item.group_name})" for item in report.group_metrics]
        maes = [item.mae for item in report.group_metrics]
        rmses = [item.rmse for item in report.group_metrics]
        mapes = [item.mape for item in report.group_metrics]

        x = np.arange(len(groups))
        width = 0.25

        fig, ax1 = plt.subplots(figsize=(12, 6))

        rects1 = ax1.bar(x - width, maes, width, label='MAE (kcal)', color='#3b82f6')
        rects2 = ax1.bar(x, rmses, width, label='RMSE (kcal)', color='#ef4444')

        ax2 = ax1.twinx()
        rects3 = ax2.bar(x + width, mapes, width, label='MAPE (%)', color='#10b981', alpha=0.85)

        ax1.set_ylabel('Absolute Error (kcal)', color='#1e293b')
        ax2.set_ylabel('Percentage Error (%)', color='#047857')
        ax1.set_title('Demographic Calorie Prediction Model Accuracy (MAE, RMSE, MAPE)', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(groups, rotation=30, ha='right', fontsize=9)

        # Merge legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        plt.tight_layout()
        plt.savefig(chart_output, dpi=200)
        plt.close()
        print(f"[Results Export] Saved accuracy bar chart to {chart_output}")
    except Exception as e:
        print(f"[Results Export] Chart generation notice: {e}")

    print("=" * 85)
    print("Stage 6 Evaluation completed successfully.")


if __name__ == "__main__":
    run_accuracy_evaluation()
