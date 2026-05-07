"""
Applique le patch joblib sur app/api/main.py
Lance : python patch_main.py
"""
import os

path = os.path.join("app", "api", "main.py")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Ajouter import joblib après import pickle
content = content.replace(
    "import pickle",
    "import pickle\nimport joblib"
)

# 2. Remplacer les deux pickle.load par joblib.load dans get_models()
old = '''def get_models():
    global _model, _pca
    if _model is None:
        with open(os.path.join(MODEL_DIR, "lightgbm.pkl"), "rb") as f: _model = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "pca_512.pkl"),  "rb") as f: _pca   = pickle.load(f)
    return _model, _pca'''

new = '''def get_models():
    global _model, _pca
    if _model is None:
        _model = joblib.load(os.path.join(MODEL_DIR, "lightgbm.pkl"))
        _pca   = joblib.load(os.path.join(MODEL_DIR, "pca_512.pkl"))
        print(f"[SkinSight]  LightGBM chargé  : {type(_model).__name__}")
        print(f"[SkinSight]  PCA chargé        : n_components={_pca.n_components_}")
    return _model, _pca'''

if old in content:
    content = content.replace(old, new)
    print(" Patch get_models() appliqué")
else:
    print("  Bloc get_models() non trouvé — vérifier manuellement")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(" app/api/main.py mis à jour")
print()
print("Lance maintenant :")
print("  uvicorn app.api.main:app --reload --port 8000")