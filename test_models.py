"""
SkinSight AI — Script de diagnostic
Lance : python test_models.py
"""
import os, sys

BASE = r"C:\Users\nasri\OneDrive\Desktop\Projects\SkinSightAI"
MODEL_DIR = os.path.join(BASE, "models")

print("=" * 60)
print("ÉTAPE 1 — Vérification des fichiers .pkl")
print("=" * 60)

for fname in ["lightgbm.pkl", "pca_512.pkl", "random_forest.pkl"]:
    path = os.path.join(MODEL_DIR, fname)
    exists = os.path.exists(path)
    size   = f"{os.path.getsize(path)/1e6:.1f} MB" if exists else "—"
    print(f"  {'✅' if exists else '❌'}  {fname:<25} {size}")

print()
print("=" * 60)
print("ÉTAPE 2 — Chargement LightGBM + PCA")
print("=" * 60)

try:
    import pickle
    with open(os.path.join(MODEL_DIR, "lightgbm.pkl"), "rb") as f:
        lgbm = pickle.load(f)
    print(f"  ✅ LightGBM chargé  → {type(lgbm).__name__}")
    print(f"     Classes         : {lgbm.classes_}")
    print(f"     n_estimators    : {lgbm.n_estimators}")
except Exception as e:
    print(f"  ❌ LightGBM ERREUR : {e}")
    sys.exit(1)

try:
    with open(os.path.join(MODEL_DIR, "pca_512.pkl"), "rb") as f:
        pca = pickle.load(f)
    print(f"  ✅ PCA chargé       → {type(pca).__name__}")
    print(f"     n_components    : {pca.n_components_}")
    print(f"     n_features_in   : {pca.n_features_in_}")
    print(f"     variance totale : {sum(pca.explained_variance_ratio_)*100:.2f}%")
except Exception as e:
    print(f"  ❌ PCA ERREUR : {e}")
    sys.exit(1)

print()
print("=" * 60)
print("ÉTAPE 3 — Import TensorFlow")
print("=" * 60)

try:
    import tensorflow as tf
    print(f"  ✅ TensorFlow {tf.__version__}")
    gpus = tf.config.list_physical_devices('GPU')
    print(f"     GPU détecté     : {'Oui' if gpus else 'Non (CPU uniquement)'}")
except ImportError:
    print("  ❌ TensorFlow NON INSTALLÉ — pip install tensorflow")
    sys.exit(1)
except Exception as e:
    print(f"  ❌ TensorFlow ERREUR : {e}")
    sys.exit(1)

print()
print("=" * 60)
print("ÉTAPE 4 — Chargement des 3 CNN (peut prendre 30–60s)")
print("=" * 60)

try:
    from tensorflow.keras.applications import MobileNetV2
    mob = MobileNetV2(weights="imagenet", include_top=False, pooling="avg")
    print(f"  ✅ MobileNetV2 chargé  → output shape : {mob.output_shape}")
except Exception as e:
    print(f"  ❌ MobileNetV2 ERREUR : {e}")

try:
    from tensorflow.keras.applications import DenseNet121
    den = DenseNet121(weights="imagenet", include_top=False, pooling="avg")
    print(f"  ✅ DenseNet121 chargé  → output shape : {den.output_shape}")
except Exception as e:
    print(f"  ❌ DenseNet121 ERREUR : {e}")

try:
    from tensorflow.keras.applications import InceptionV3
    inc = InceptionV3(weights="imagenet", include_top=False, pooling="avg", input_shape=(299,299,3))
    print(f"  ✅ InceptionV3 chargé  → output shape : {inc.output_shape}")
except Exception as e:
    print(f"  ❌ InceptionV3 ERREUR : {e}")

print()
print("=" * 60)
print("ÉTAPE 5 — Test pipeline complet sur image synthétique")
print("=" * 60)

try:
    import numpy as np
    from PIL import Image
    from tensorflow.keras.preprocessing.image import img_to_array
    from tensorflow.keras.applications.mobilenet_v2  import preprocess_input as pm
    from tensorflow.keras.applications.densenet       import preprocess_input as pd
    from tensorflow.keras.applications.inception_v3   import preprocess_input as pi

    # Image aléatoire 224×224 RGB
    fake_img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))

    def prep(img, size, fn):
        arr = img_to_array(img.resize(size).convert("RGB"))
        return fn(np.expand_dims(arr, 0))

    f_mob = mob.predict(prep(fake_img, (224,224), pm), verbose=0).flatten()
    f_den = den.predict(prep(fake_img, (224,224), pd), verbose=0).flatten()
    f_inc = inc.predict(prep(fake_img, (299,299), pi), verbose=0).flatten()

    feats = np.concatenate([f_mob, f_den, f_inc]).reshape(1, -1)
    print(f"  ✅ Features concaténées : shape = {feats.shape}  (attendu : (1, 4352))")

    if feats.shape[1] != pca.n_features_in_:
        print(f"  ❌ SHAPE MISMATCH : features={feats.shape[1]} mais PCA attend {pca.n_features_in_}")
        print("     → Le PCA a été entraîné sur une dim différente. Ré-entraîner le PCA.")
        sys.exit(1)

    reduced = pca.transform(feats)
    print(f"  ✅ PCA transform OK     : shape = {reduced.shape}  (attendu : (1, 512))")

    proba = lgbm.predict_proba(reduced)[0]
    CLASSES = ["saine","acne_inflammatoire","acne_non_inflammatoire","rosacee","hyperpigmentation"]
    idx = np.argmax(proba)
    print(f"  ✅ LightGBM predict OK  : classe = {CLASSES[idx]} ({proba[idx]*100:.1f}%)")

    print()
    print("=" * 60)
    print("🎉  PIPELINE COMPLET FONCTIONNEL — /predict devrait marcher")
    print("=" * 60)

except Exception as e:
    import traceback
    print(f"  ❌ ERREUR pipeline : {e}")
    print()
    traceback.print_exc()
    print()
    print("  → Colle ce traceback dans le chat pour qu'on règle ça.")