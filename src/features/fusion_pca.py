"""
SkinSight AI — Fusion des features (MobileNetV2 + DenseNet121 + InceptionV3) + PCA
Output : vecteur réduit de 512 dimensions prêt pour Random Forest / LightGBM
"""
import numpy as np
import joblib
from pathlib import Path
from sklearn.decomposition import PCA

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, DenseNet121, InceptionV3
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.models import Model


# ─── Construction des extracteurs ─────────────────────────────────────────────

def _build_extractor(base_model) -> Model:
    """Retire la tête de classification, ajoute un GAP."""
    x = GlobalAveragePooling2D()(base_model.output)
    return Model(inputs=base_model.input, outputs=x)


def build_extractors():
    """Retourne les 3 extracteurs (weights ImageNet, frozen)."""
    print("[SkinSight] Chargement MobileNetV2...")
    mobilenet = _build_extractor(
        MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    )

    print("[SkinSight] Chargement DenseNet121...")
    densenet = _build_extractor(
        DenseNet121(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    )

    print("[SkinSight] Chargement InceptionV3...")
    inception = _build_extractor(
        InceptionV3(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    )

    for m in [mobilenet, densenet, inception]:
        m.trainable = False

    return mobilenet, densenet, inception


# ─── Extraction des features pour un dataset ─────────────────────────────────

def extract_features(dataset, extractors: tuple) -> np.ndarray:
    """
    Extrait et concatène les features des 3 modèles.
    dataset : tf.data.Dataset qui renvoie (images, labels)
    Retourne : (features_concat [N, 4352], labels [N,])
    """
    mobilenet, densenet, inception = extractors
    all_feats, all_labels = [], []

    for batch_imgs, batch_labels in dataset:
        f_mob  = mobilenet(batch_imgs, training=False).numpy()   # (B, 1280)
        f_den  = densenet(batch_imgs,  training=False).numpy()   # (B, 1024)
        f_inc  = inception(batch_imgs, training=False).numpy()   # (B, 2048)

        concat = np.concatenate([f_mob, f_den, f_inc], axis=1)  # (B, 4352)
        all_feats.append(concat)
        all_labels.append(batch_labels.numpy())

    return np.vstack(all_feats), np.concatenate(all_labels)


# ─── PCA : réduction 4352 → 512 ───────────────────────────────────────────────

def fit_pca(X_train: np.ndarray, n_components: int = 512, save_path: str = "models/pca_512.pkl") -> PCA:
    print(f"[SkinSight] PCA : {X_train.shape[1]}D → {n_components}D ...")
    pca = PCA(n_components=n_components, random_state=42)
    pca.fit(X_train)
    variance_explained = pca.explained_variance_ratio_.sum()
    print(f"  Variance expliquée : {variance_explained:.2%}")
    joblib.dump(pca, save_path)
    print(f"  PCA sauvegardé → {save_path}")
    return pca


def apply_pca(X: np.ndarray, pca: PCA) -> np.ndarray:
    return pca.transform(X)


def load_pca(path: str = "models/pca_512.pkl") -> PCA:
    return joblib.load(path)
