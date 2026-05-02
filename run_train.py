import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import lightgbm as lgb
import joblib
import time

MODELS_DIR = Path("models")
CLASSES = ["saine", "acne_inflammatoire", "acne_non_inflammatoire", "rosacee", "hyperpigmentation"]

# Charger les features
print(" Chargement des features...")
X_train = np.load(MODELS_DIR / "X_train.npy")
y_train = np.load(MODELS_DIR / "y_train.npy")
X_val   = np.load(MODELS_DIR / "X_val.npy")
y_val   = np.load(MODELS_DIR / "y_val.npy")
X_test  = np.load(MODELS_DIR / "X_test.npy")
y_test  = np.load(MODELS_DIR / "y_test.npy")
print(f"  Train : {X_train.shape} | Val : {X_val.shape} | Test : {X_test.shape}")

# ─── Random Forest ────────────────────────────────────────────────────
print("\n Entraînement Random Forest...")
t0 = time.time()
rf = RandomForestClassifier(n_estimators=200, max_depth=None, n_jobs=-1, random_state=42)
rf.fit(X_train, y_train)
rf_time = time.time() - t0

rf_val_pred  = rf.predict(X_val)
rf_test_pred = rf.predict(X_test)
rf_val_acc   = accuracy_score(y_val, rf_val_pred)
rf_test_acc  = accuracy_score(y_test, rf_test_pred)
rf_f1        = f1_score(y_test, rf_test_pred, average="weighted")

joblib.dump(rf, MODELS_DIR / "random_forest.pkl")
print(f"  Val Accuracy  : {rf_val_acc:.4f}")
print(f"  Test Accuracy : {rf_test_acc:.4f}")
print(f"  F1 Score      : {rf_f1:.4f}")
print(f"  Temps         : {rf_time:.1f}s")

# ─── LightGBM ─────────────────────────────────────────────────────────
print("\n Entraînement LightGBM...")
t0 = time.time()
lgbm = lgb.LGBMClassifier(
    n_estimators=500, learning_rate=0.05,
    num_leaves=63, n_jobs=-1, random_state=42, verbose=-1
)
lgbm.fit(X_train, y_train, eval_set=[(X_val, y_val)])
lgbm_time = time.time() - t0

lgbm_val_pred  = lgbm.predict(X_val)
lgbm_test_pred = lgbm.predict(X_test)
lgbm_val_acc   = accuracy_score(y_val, lgbm_val_pred)
lgbm_test_acc  = accuracy_score(y_test, lgbm_test_pred)
lgbm_f1        = f1_score(y_test, lgbm_test_pred, average="weighted")

joblib.dump(lgbm, MODELS_DIR / "lightgbm.pkl")
print(f"  Val Accuracy  : {lgbm_val_acc:.4f}")
print(f"  Test Accuracy : {lgbm_test_acc:.4f}")
print(f"  F1 Score      : {lgbm_f1:.4f}")
print(f"  Temps         : {lgbm_time:.1f}s")

# ─── Comparaison finale ───────────────────────────────────────────────
print("\n" + "="*55)
print(" COMPARAISON FINALE")
print("="*55)
print(f"{'Modèle':<20} {'Val Acc':>10} {'Test Acc':>10} {'F1':>10} {'Temps':>8}")
print("-"*55)
print(f"{'Random Forest':<20} {rf_val_acc:>10.4f} {rf_test_acc:>10.4f} {rf_f1:>10.4f} {rf_time:>7.1f}s")
print(f"{'LightGBM':<20} {lgbm_val_acc:>10.4f} {lgbm_test_acc:>10.4f} {lgbm_f1:>10.4f} {lgbm_time:>7.1f}s")

winner = "LightGBM" if lgbm_test_acc > rf_test_acc else "Random Forest"
print(f"\n Meilleur modèle : {winner}")

# Rapport détaillé du meilleur
best_pred = lgbm_test_pred if winner == "LightGBM" else rf_test_pred
print(f"\n Rapport détaillé ({winner}) :")
print(classification_report(y_test, best_pred, target_names=CLASSES))