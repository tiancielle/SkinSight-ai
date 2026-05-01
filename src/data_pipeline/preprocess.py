"""
SkinSight AI — Prétraitement des images
Resize, normalisation ImageNet, augmentation.
"""
import numpy as np
from pathlib import Path
from PIL import Image
import tensorflow as tf
import yaml


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


CFG = load_config()
IMG_SIZE = tuple(CFG["data"]["image_size"])
MEAN = np.array([0.485, 0.456, 0.406])
STD  = np.array([0.229, 0.224, 0.225])


def preprocess_image(img_path: str, augment: bool = False) -> np.ndarray:
    """Charge une image et applique le prétraitement standard."""
    img = Image.open(img_path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    x = np.array(img, dtype=np.float32) / 255.0

    if augment:
        x = _augment(x)

    x = (x - MEAN) / STD
    return x.astype(np.float32)


def _augment(x: np.ndarray) -> np.ndarray:
    """Augmentations légères : flip, brightness, rotation."""
    # Horizontal flip (50%)
    if np.random.rand() > 0.5:
        x = np.fliplr(x)

    # Brightness ±20%
    factor = 1.0 + np.random.uniform(-0.2, 0.2)
    x = np.clip(x * factor, 0, 1)

    # Rotation légère via tf (±15°)
    x_tf = tf.image.rot90(
        tf.constant(x[np.newaxis]),
        k=np.random.randint(0, 4)
    ).numpy()[0]
    return x_tf


def build_dataset(data_dir: str, augment: bool = False, batch_size: int = 32):
    """
    Construit un tf.data.Dataset à partir d'un dossier structuré :
    data_dir/
        saine/
        acne_inflammatoire/
        ...
    """
    classes = CFG["data"]["classes"]
    class_to_idx = {c: i for i, c in enumerate(classes)}

    paths, labels = [], []
    for cls in classes:
        cls_dir = Path(data_dir) / cls
        if not cls_dir.exists():
            continue
        for img_path in cls_dir.glob("*.jpg"):
            paths.append(str(img_path))
            labels.append(class_to_idx[cls])

    def _load(path, label):
        img = tf.py_function(
            lambda p: preprocess_image(p.numpy().decode(), augment),
            [path], tf.float32
        )
        img.set_shape([*IMG_SIZE, 3])
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.shuffle(buffer_size=len(paths), seed=CFG["project"]["seed"])
    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds, class_to_idx
