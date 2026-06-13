import torch
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from constants import ALL_FILMS, FILM_FEATURES, N_COMPONENTS

def get_training_tensors(ratings: pd.DataFrame):
    # ── Build mask-augmented matrix for PCA ──────────────────────────────────────
    ratings_filled = ratings.fillna(0).values.astype(float)
    seen_mask      = (~ratings.isna()).astype(float).values
    R = np.concatenate([ratings_filled, seen_mask], axis=1)  # (n_users, 24)

    # ── PCA taste compression ─────────────────────────────────────────────────────
    scaler = StandardScaler()
    R_scaled = scaler.fit_transform(R)
    pca = PCA(n_components=N_COMPONENTS)
    taste = pca.fit_transform(R_scaled)

    # ── Build training examples ───────────────────────────────────────────────────
    rows, targets = [], []
    for i, user in enumerate(ratings.index):
        for film in ALL_FILMS:
            rating = ratings.loc[user, film]
            if pd.isna(rating):
                continue
            x = np.concatenate([taste[i], FILM_FEATURES[film]])
            rows.append(x)
            targets.append(rating)

    X = torch.tensor(np.array(rows), dtype=torch.float32)
    y = torch.tensor(targets, dtype=torch.float32).unsqueeze(1)
    print(f"Training examples: {len(X)}")

    return X, y, scaler, pca
