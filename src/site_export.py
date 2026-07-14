"""Writes model/pipeline.json — everything the website needs, from one source
of truth: the film catalogue with index coordinates, the default Odyssey
position, the rating gate, and the Oscar model's coefficients."""
import json
import os

from constants import ALL_FILMS, FILM_LABELS, MIN_RATINGS, MODEL_DIR, NOLAN_INDEX, ODYSSEY_DEFAULT


def write_pipeline(oscar_coeffs: dict):
    pipeline = {
        "films": [
            {
                "key": film,
                "label": FILM_LABELS[film],
                "fabula": NOLAN_INDEX[film][0],
                "syuzhet": NOLAN_INDEX[film][1],
            }
            for film in ALL_FILMS
        ],
        "odyssey": ODYSSEY_DEFAULT,
        "min_ratings": MIN_RATINGS,
        "oscars": {"coeffs": oscar_coeffs},
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    output_path = os.path.join(MODEL_DIR, "pipeline.json")
    with open(output_path, "w") as f:
        json.dump(pipeline, f, indent=2)

    print(f"Exported {output_path}")
