"""
SkinSight AI — Classifieurs : Random Forest vs LightGBM
Input  : vecteur PCA 512D
Output : classe parmi {saine, acne_inflammatoire, acne_non_inflammatoire, rosacee, hyperpigmentation}
"""
import numpy as np
import joblib
import yaml
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix
)
import lightgbm as lgb


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


CFG = load_config()
CLASSES = CFG["data"]["classes"]


# ─── Random Forest ────────────────────────────────────────────────────────────

def train_random_forest(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
    rf_cfg = CFG["classifiers"]["random_forest"]
    print("[SkinSight] Entraînement Random Forest...")
    model = RandomForestClassifier(
        n_estimators=rf_cfg["n_estimators"],
        max_depth=rf_cfg["max_depth"],
        min_samples_split=rf_cfg["min_samples_split"],
        class_weight=rf_cfg["class_weight"],
        n_jobs=rf_cfg["n_jobs"],
        random_state=CFG["project"]["seed"],
        verbose=1
    )
    model.fit(X_train, y_train)
    joblib.dump(model, "models/rf_model.pkl")
    print("  Sauvegardé → models/rf_model.pkl")
    return model


# ─── LightGBM ─────────────────────────────────────────────────────────────────

def train_lightgbm(X_train: np.ndarray, y_train: np.ndarray,
                   X_val: np.ndarray,   y_val: np.ndarray) -> lgb.LGBMClassifier:
    lgb_cfg = CFG["classifiers"]["lightgbm"]
    print("[SkinSight] Entraînement LightGBM...")
    model = lgb.LGBMClassifier(
        n_estimators=lgb_cfg["n_estimators"],
        learning_rate=lgb_cfg["learning_rate"],
        max_depth=lgb_cfg["max_depth"],
        num_leaves=lgb_cfg["num_leaves"],
        class_weight=lgb_cfg["class_weight"],
        n_jobs=lgb_cfg["n_jobs"],
        random_state=CFG["project"]["seed"],
        verbosity=-1
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(50)]
    )
    joblib.dump(model, "models/lgbm_model.pkl")
    print("  Sauvegardé → models/lgbm_model.pkl")
    return model


# ─── Évaluation commune ────────────────────────────────────────────────────────

def evaluate(model, X_test: np.ndarray, y_test: np.ndarray,
             model_name: str = "Model") -> dict:
    """Retourne accuracy, F1-macro, AUC-ROC et affiche le rapport complet."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    acc  = accuracy_score(y_test, y_pred)
    f1   = f1_score(y_test, y_pred, average="macro")
    auc  = roc_auc_score(y_test, y_prob, multi_class="ovr", average="macro")
    cm   = confusion_matrix(y_test, y_pred)

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"  Accuracy  : {acc:.4f}")
    print(f"  F1-macro  : {f1:.4f}")
    print(f"  AUC-ROC   : {auc:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=CLASSES)}")

    metrics = {
        "model": model_name,
        "accuracy": round(acc, 4),
        "f1_macro": round(f1, 4),
        "auc_roc":  round(auc, 4),
        "confusion_matrix": cm.tolist()
    }

    out_path = Path("models") / f"metrics_{model_name.lower().replace(' ', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Métriques → {out_path}")
    return metrics


def compare_models(metrics_rf: dict, metrics_lgbm: dict):
    """Affiche un tableau comparatif RF vs LightGBM."""
    print("\n" + "="*55)
    print(f"  {'Métrique':<18} {'Random Forest':>16} {'LightGBM':>14}")
    print("="*55)
    for key in ["accuracy", "f1_macro", "auc_roc"]:
        print(f"  {key:<18} {metrics_rf[key]:>16.4f} {metrics_lgbm[key]:>14.4f}")
    print("="*55)
    winner = "Random Forest" if metrics_rf["f1_macro"] > metrics_lgbm["f1_macro"] else "LightGBM"
    print(f"  Meilleur F1-macro : {winner}")
