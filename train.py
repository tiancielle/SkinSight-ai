"""
SkinSight AI — Pipeline d'entraînement complet
Usage : python train.py --data_dir data/processed/ --mode full
"""
import argparse
import numpy as np
from pathlib import Path

# ── Imports locaux (ajouter src/ au path si besoin) ───────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_pipeline.preprocess import build_dataset, load_config
from features.fusion_pca import build_extractors, extract_features, fit_pca, apply_pca
from classifiers.train_pipeline import (
    train_random_forest, train_lightgbm, evaluate, compare_models
)


def run(data_dir: str, mode: str = "full"):
    CFG = load_config("config.yaml")

    print("\n" + "="*60)
    print("  SkinSight AI — Pipeline d'entraînement")
    print("="*60)

    # ── Étape 1 : Datasets ────────────────────────────────────────────────────
    print("\n[1/5] Construction des datasets...")
    train_ds, class_to_idx = build_dataset(f"{data_dir}/train", augment=True)
    val_ds,   _            = build_dataset(f"{data_dir}/val",   augment=False)
    test_ds,  _            = build_dataset(f"{data_dir}/test",  augment=False)
    print(f"  Classes : {class_to_idx}")

    # ── Étape 2 : Extraction des features ─────────────────────────────────────
    print("\n[2/5] Extraction des features CNN (3 modèles)...")
    extractors = build_extractors()
    X_train, y_train = extract_features(train_ds, extractors)
    X_val,   y_val   = extract_features(val_ds,   extractors)
    X_test,  y_test  = extract_features(test_ds,  extractors)
    print(f"  Shape features brutes : {X_train.shape}")  # (N, 4352)

    # ── Étape 3 : PCA ─────────────────────────────────────────────────────────
    print("\n[3/5] Réduction PCA 4352 → 512D...")
    pca = fit_pca(X_train, n_components=CFG["features"]["pca_components"])
    X_train_r = apply_pca(X_train, pca)
    X_val_r   = apply_pca(X_val,   pca)
    X_test_r  = apply_pca(X_test,  pca)
    print(f"  Shape réduite : {X_train_r.shape}")        # (N, 512)

    # ── Étape 4 : Entraînement des classifieurs ────────────────────────────────
    print("\n[4/5] Entraînement des classifieurs...")

    rf_model   = train_random_forest(X_train_r, y_train)
    lgbm_model = train_lightgbm(X_train_r, y_train, X_val_r, y_val)

    # ── Étape 5 : Évaluation et comparaison ───────────────────────────────────
    print("\n[5/5] Évaluation sur le jeu de test...")
    metrics_rf   = evaluate(rf_model,   X_test_r, y_test, "Random Forest")
    metrics_lgbm = evaluate(lgbm_model, X_test_r, y_test, "LightGBM")

    compare_models(metrics_rf, metrics_lgbm)
    print("\n  Pipeline terminé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SkinSight AI Training Pipeline")
    parser.add_argument("--data_dir", default="data/processed/", help="Dossier des données")
    parser.add_argument("--mode",     default="full", choices=["full", "features_only", "clf_only"])
    args = parser.parse_args()
    run(args.data_dir, args.mode)
