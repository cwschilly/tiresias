import os
import json
import torch

from constants import INPUT_DIM, ALL_FILMS, N_COMPONENTS, FILM_FEATURES, N_FILM_FEATURES, OUTPUT_DIR

def export_model(model):
    model.eval()
    dummy = torch.zeros(1, INPUT_DIM)
    output_path = os.path.join(OUTPUT_DIR, "model.onnx")
    torch.onnx.export(
        model, dummy, output_path,
        input_names=["input"], output_names=["rating"],
        dynamic_axes={"input": {0: "batch"}},
        opset_version=18
    )
    print(f"Exported {output_path}")

def write_pipeline(scaler, pca):
    pipeline = {
        "film_cols":       ALL_FILMS,
        "n_components":    N_COMPONENTS,
        "scaler_mean":     scaler.mean_.tolist(),
        "scaler_std":      scaler.scale_.tolist(),
        "pca_mean":        pca.mean_.tolist(),
        "pca_components":  pca.components_.tolist(),
        "film_features":   FILM_FEATURES,
        "n_film_features": N_FILM_FEATURES,
        "rating_scale":    "0.5-5.0",  # stored for reference
    }

    output_path = os.path.join(OUTPUT_DIR, "pipeline.json")
    with open(output_path, "w") as f:
        json.dump(pipeline, f, indent=2)

    print(f"Exported {output_path}")
