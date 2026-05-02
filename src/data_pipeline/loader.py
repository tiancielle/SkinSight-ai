"""
src/data_pipeline/loader.py
Charge les images depuis les CSV de splits et les prépare
pour l'extraction de features CNN.
"""

import csv
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict
import cv2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from sklearn.preprocessing import LabelEncoder

# ─── Constantes ───────────────────────────────────────────────────────
IMG_SIZE = (224, 224)
CLASSES = [
    "saine",
    "acne_inflammatoire",
    "acne_non_inflammatoire",
    "rosacee",
    "hyperpigmentation",
]


def load_csv_split(csv_path: str) -> Tuple[List[str], List[str]]:
    """Lit un CSV split et retourne (filepaths, labels)."""
    filepaths, labels = [], []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filepaths.append(row["filepath"])
            labels.append(row["label"])
    return filepaths, labels


def load_image(path: str, size: tuple = IMG_SIZE) -> np.ndarray:
    """
    Charge une image depuis le disque.
    Retourne un tableau (224, 224, 3) normalisé ImageNet.
    """
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image introuvable : {path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, size, interpolation=cv2.INTER_LANCZOS4)
    img = img.astype("float32")
    return preprocess_input(img)   # normalisation ImageNet


def load_batch(
    filepaths: List[str],
    labels: List[str],
    batch_size: int = 32,
    verbose: bool = True
):
    """
    Générateur : yield (X_batch, y_batch) jusqu'à épuisement.
    X_batch : (batch_size, 224, 224, 3)
    y_batch : liste de labels string
    """
    n = len(filepaths)
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        batch_imgs, batch_labels = [], []
        for path, label in zip(filepaths[start:end], labels[start:end]):
            try:
                img = load_image(path)
                batch_imgs.append(img)
                batch_labels.append(label)
            except Exception as e:
                print(f"  Ignoré ({e}) : {path}")
        if verbose:
            print(f"  Batch {start//batch_size + 1} : {len(batch_imgs)} images chargées")
        yield np.array(batch_imgs), batch_labels


def load_all(
    csv_path: str,
    batch_size: int = 32,
    verbose: bool = True
) -> Tuple[np.ndarray, np.ndarray, LabelEncoder]:
    """
    Charge toutes les images d'un split en mémoire.
    Retourne (X, y_encoded, label_encoder).
    Attention : ne pas utiliser sur de très grands datasets.
    """
    filepaths, labels = load_csv_split(csv_path)
    print(f" Chargement de {len(filepaths)} images depuis {csv_path}")

    all_imgs, all_labels = [], []
    for X_batch, y_batch in load_batch(filepaths, labels, batch_size, verbose):
        all_imgs.append(X_batch)
        all_labels.extend(y_batch)

    X = np.concatenate(all_imgs, axis=0)

    le = LabelEncoder()
    le.fit(CLASSES)
    y = le.transform(all_labels)

    print(f" X shape : {X.shape} | Classes : {le.classes_}")
    return X, y, le


def get_class_distribution(csv_path: str) -> Dict[str, int]:
    """Retourne le nombre d'images par classe dans un split."""
    _, labels = load_csv_split(csv_path)
    dist = {}
    for l in labels:
        dist[l] = dist.get(l, 0) + 1
    return dist


if __name__ == "__main__":
    # Test rapide
    dist = get_class_distribution("data/splits/train.csv")
    print("Distribution train :", dist)