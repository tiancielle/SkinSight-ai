from src.data_pipeline.augment import augment_train_split
augment_train_split(
    splits_dir='data/splits',
    augmented_dir='data/augmented',
    target_per_class=1000
)