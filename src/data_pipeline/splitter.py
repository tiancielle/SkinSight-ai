"""
src/data_pipeline/splitter.py
Découpe les données raw en splits train / val / test
et génère un CSV récapitulatif par split.
"""

import os, shutil, random, csv
from pathlib import Path
import yaml

# ─── Config ──────────────────────────────────────────────────────────
CONFIG_PATH = Path("config.yaml")

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

# ─── Splitter principal ───────────────────────────────────────────────
def split_dataset(
    raw_dir: str = "data/raw",
    splits_dir: str = "data/splits",
    ratios: tuple = (0.7, 0.15, 0.15),
    seed: int = 42,
    extensions: tuple = (".jpg", ".jpeg", ".png", ".bmp")
):
    """
    Structure attendue dans raw_dir :
        raw/
          saine/
          acne_inflammatoire/
          acne_non_inflammatoire/
          rosacee/
          hyperpigmentation/

    Résultat dans splits_dir :
        splits/
          train/  val/  test/
          train.csv  val.csv  test.csv
    """
    assert abs(sum(ratios) - 1.0) < 1e-6, "Les ratios doivent sommer à 1"
    random.seed(seed)

    raw_path = Path(raw_dir)
    splits_path = Path(splits_dir)

    for split in ["train", "val", "test"]:
        (splits_path / split).mkdir(parents=True, exist_ok=True)

    csv_data = {"train": [], "val": [], "test": []}
    stats = {}

    for class_dir in sorted(raw_path.iterdir()):
        if not class_dir.is_dir(): continue
        label = class_dir.name

        images = [
            p for p in class_dir.iterdir()
            if p.suffix.lower() in extensions
        ]
        random.shuffle(images)

        n = len(images)
        n_train = int(n * ratios[0])
        n_val   = int(n * ratios[1])

        splits_map = {
            "train": images[:n_train],
            "val":   images[n_train:n_train + n_val],
            "test":  images[n_train + n_val:]
        }

        stats[label] = {}
        for split, files in splits_map.items():
            dest_dir = splits_path / split / label
            dest_dir.mkdir(parents=True, exist_ok=True)
            for src in files:
                shutil.copy2(src, dest_dir / src.name)
                csv_data[split].append({
                    "filepath": str(dest_dir / src.name),
                    "label": label
                })
            stats[label][split] = len(files)

    for split, rows in csv_data.items():
        csv_path = splits_path / f"{split}.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["filepath", "label"])
            writer.writeheader()
            writer.writerows(rows)

    print("\n Split terminé — Résumé :")
    print(f"{'Classe':<30} {'Train':>8} {'Val':>8} {'Test':>8} {'Total':>8}")
    print("-" * 64)
    for label, s in stats.items():
        total = sum(s.values())
        print(f"{label:<30} {s['train']:>8} {s['val']:>8} {s['test']:>8} {total:>8}")

    return stats


if __name__ == "__main__":
    cfg = load_config()
    split_dataset(
        raw_dir=cfg["data"]["raw_dir"],
        splits_dir=cfg["data"]["splits_dir"],
        ratios=tuple(cfg["data"]["split_ratios"]),
        seed=cfg["seed"]
    )