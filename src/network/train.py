import os
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from .mlp import RatingMLP
from constants import OUTPUT_DIR, NUM_EPOCHS

def train_model(X: torch.Tensor, y: torch.Tensor, val_split: float = 0.2) -> RatingMLP:
    # Train/val split
    n_val  = max(1, int(len(X) * val_split))
    idx    = torch.randperm(len(X))
    X_train, y_train = X[idx[n_val:]], y[idx[n_val:]]
    X_val,   y_val   = X[idx[:n_val]], y[idx[:n_val]]

    model   = RatingMLP()
    opt     = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    train_losses, val_losses = [], []

    for epoch in range(NUM_EPOCHS):
        model.train()
        train_loss = loss_fn(model(X_train), y_train)
        opt.zero_grad(); train_loss.backward(); opt.step()

        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(X_val), y_val)

        train_losses.append(train_loss.item() ** 0.5)
        val_losses.append(val_loss.item() ** 0.5)

        if epoch % 500 == 0:
            print(f"Epoch {epoch:4d}  train RMSE={train_losses[-1]:.4f}  val RMSE={val_losses[-1]:.4f}")

    _plot_losses(train_losses, val_losses)
    return model


def _plot_losses(train_losses: list, val_losses: list) -> None:
    epochs = range(len(train_losses))
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, train_losses, label="Train RMSE")
    plt.plot(epochs, val_losses,   label="Val RMSE")
    plt.xlabel("Epoch")
    plt.ylabel("RMSE")
    plt.title("Training vs Validation Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "loss.png"), dpi=150)
    plt.close()
