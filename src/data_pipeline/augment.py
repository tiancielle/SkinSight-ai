"""
src/data_pipeline/augment.py
Augmentation des images pour équilibrer les classes sous-représentées.
Génère les images augmentées dans data/augmented/.
"""

import cv2
import numpy as np
import random
import csv
from pathlib import Path
from typing import List, Tuple


# ─── Transformations unitaires ────────────────────────────────────────

def random_flip(img: np.ndarray) -> np.ndarray:
    """Flip horizontal aléatoire."""
    if random.random() > 0.5:
        img = cv2.flip(img, 1)
    return img


def random_rotation(img: np.ndarray, max_angle: int = 20) -> np.ndarray:
    """Rotation aléatoire dans [-max_angle, +max_angle] degrés."""
    angle = random.uniform(-max_angle, max_angle)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def random_brightness(img: np.ndarray, factor_range: tuple = (0.7, 1.3)) -> np.ndarray:
    """Variation aléatoire de luminosité."""
    factor = random.uniform(*factor_range)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype("float32")
    hsv[..., 2] = np.clip(hsv[..., 2] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2RGB)


def random_zoom(img: np.ndarray, zoom_range: tuple = (0.85, 1.15)) -> np.ndarray:
    """Zoom in/out aléatoire avec recadrage au centre."""
    h, w = img.shape[:2]
    factor = random.uniform(*zoom_range)
    new_h, new_w = int(h * factor), int(w * factor)
    resized = cv2.resize(img, (new_w, new_h))
    if factor > 1.0:   # zoom in → crop
        y0 = (new_h - h) // 2
        x0 = (new_w - w) // 2
        return resized[y0:y0+h, x0:x0+w]
    else:              # zoom out → pad
        pad_h = (h - new_h) // 2
        pad_w = (w - new_w) // 2
        canvas = np.zeros_like(img)
        canvas[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized
        return canvas


def random_gaussian_noise(img: np.ndarray, std: float = 10.0) -> np.ndarray:
    """Ajout de bruit gaussien léger."""
    noise = np.random.normal(0, std, img.shape).astype("float32")
    return np.clip(img.astype("float32") + noise, 0, 255).astype("uint8")


def augment_image(img: np.ndarray) -> np.ndarray:
    """Applique un pipeline d'augmentation complet sur une image."""
    img = random_flip(img)
    img = random_rotation(img)
    img = random_brightness(img)
    img = random_zoom(img)
    img = random_gaussian_noise(img)
    return img


# ─── Augmentation par classe ──────────────────────────────────────────

def augment_class(
    src_dir: Path,
    dst_dir: Path,
    target_count: int,
    label: str,
) -> List[dict]:
    """
    Augmente les images d'une classe jusqu'à atteindre target_count.
    Retourne la liste des nouvelles entrées (filepath, label).
    """
    extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    images = [p for p in src_dir.iterdir() if p.suffix.lower() in extensions]
    current = len(images)

    if current >= target_count:
        print(f"  {label}: {current} images — aucune augmentation nécessaire")
        return []

    dst_dir.mkdir(parents=True, exist_ok=True)
    needed = target_count - current
    new_entries = []

    for i in range(needed):
        src = random.choice(images)
        img = cv2.imread(str(src))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        aug = augment_image(img)
        out_path = dst_dir / f"aug_{i:05d}_{src.name}"
        cv2.imwrite(str(out_path), cv2.cvtColor(aug, cv2.COLOR_RGB2BGR))
        new_entries.append({"filepath": str(out_path), "label": label})

    print(f"  {label}: {current} → {current + needed} images (+{needed} augmentées)")
    return new_entries


def augment_train_split(
    splits_dir: str = "data/splits",
    augmented_dir: str = "data/augmented",
    target_per_class: int = 1000,
):
    """
    Équilibre le split train en augmentant les classes minoritaires.
    Met à jour data/splits/train.csv avec les nouvelles images.
    """
    splits_path = Path(splits_dir)
    aug_path = Path(augmented_dir)
    train_csv = splits_path / "train.csv"

    # Lire le CSV train actuel
    existing = []
    class_dirs = {}
    with open(train_csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.append(row)
            label = row["label"]
            if label not in class_dirs:
                class_dirs[label] = Path(row["filepath"]).parent

    # Compter par classe
    counts = {}
    for row in existing:
        counts[row["label"]] = counts.get(row["label"], 0) + 1

    print(f"\n Augmentation — cible : {target_per_class} images/classe")
    all_new = []
    for label, src_dir in class_dirs.items():
        dst_dir = aug_path / label
        new_entries = augment_class(src_dir, dst_dir, target_per_class, label)
        all_new.extend(new_entries)

    # Réécrire le CSV avec les nouvelles images
    all_rows = existing + all_new
    with open(train_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filepath", "label"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n train.csv mis à jour : {len(all_rows)} images au total")


if __name__ == "__main__":
    augment_train_split(
        splits_dir="data/splits",
        augmented_dir="data/augmented",
        target_per_class=1000,
    )