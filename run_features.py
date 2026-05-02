import numpy as np
import joblib
from pathlib import Path
from src.data_pipeline.loader import load_csv_split, load_image
from src.features.fusion_pca import build_extractors, extract_features, fit_pca, apply_pca
import tensorflow as tf

# Config
SPLITS_DIR  = Path("data/splits")
MODELS_DIR  = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

BATCH_SIZE  = 32
N_COMPONENTS = 512

def make_tf_dataset(csv_path, batch_size=32):
    filepaths, labels = load_csv_split(csv_path)
    label_map = {
        "saine": 0, "acne_inflammatoire": 1,
        "acne_non_inflammatoire": 2, "rosacee": 3, "hyperpigmentation": 4
    }
    y = [label_map[l] for l in labels]

    def load_fn(path, label):
        img = tf.numpy_function(
            lambda p: load_image(p.decode()),
            [path], tf.float32
        )
        img.set_shape((224, 224, 3))
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((filepaths, y))
    ds = ds.map(load_fn, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds

print("=== SkinSight AI — Extraction features ===\n")

# Charger les 3 CNN
extractors = build_extractors()

# Train
print("\n Extraction TRAIN...")
ds_train = make_tf_dataset(SPLITS_DIR / "train.csv", BATCH_SIZE)
X_train, y_train = extract_features(ds_train, extractors)
print(f"  X_train : {X_train.shape}")

# PCA
print("\n Fitting PCA...")
pca = fit_pca(X_train, N_COMPONENTS, str(MODELS_DIR / "pca_512.pkl"))
X_train_pca = apply_pca(X_train, pca)
np.save(MODELS_DIR / "X_train.npy", X_train_pca)
np.save(MODELS_DIR / "y_train.npy", y_train)
print(f"  X_train_pca : {X_train_pca.shape}")

# Val
print("\n Extraction VAL...")
ds_val = make_tf_dataset(SPLITS_DIR / "val.csv", BATCH_SIZE)
X_val, y_val = extract_features(ds_val, extractors)
X_val_pca = apply_pca(X_val, pca)
np.save(MODELS_DIR / "X_val.npy", X_val_pca)
np.save(MODELS_DIR / "y_val.npy", y_val)
print(f"  X_val_pca : {X_val_pca.shape}")

# Test
print("\n Extraction TEST...")
ds_test = make_tf_dataset(SPLITS_DIR / "test.csv", BATCH_SIZE)
X_test, y_test = extract_features(ds_test, extractors)
X_test_pca = apply_pca(X_test, pca)
np.save(MODELS_DIR / "X_test.npy", X_test_pca)
np.save(MODELS_DIR / "y_test.npy", y_test)
print(f"  X_test_pca : {X_test_pca.shape}")

print("\n Features extraites et sauvegardées dans models/")