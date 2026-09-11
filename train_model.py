"""
Food Image Detection & Classification Fine-Tuning Pipeline (Stage 4)
---------------------------------------------------------------------
Fine-tunes a PyTorch EfficientNet-B0 vision classifier / YOLOv8 pipeline on food datasets.
Outputs saved model weights checkpoint and prints epoch metrics.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from ml.train_food_classifier import train_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 4 Food Image Recognition Training")
    parser.add_argument("--epochs", type=int, default=2, help="Number of fine-tuning epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--output_path", type=str, default="ml/food_classifier_weights.pth", help="Checkpoint output path")
    args = parser.parse_args()

    print("[Stage 4 ML Training] Starting food image recognition training pipeline...")
    train_model(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, output_path=args.output_path)
