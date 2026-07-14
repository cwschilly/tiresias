"""Task 1: every Nolan film's raw position on the syuzhet/fabula plane."""
import os

from constants import ALL_FILMS, FILM_LABELS, NOLAN_INDEX, ODYSSEY_DEFAULT, OUTPUT_DIR
from plotting.style import GOLD, INK, add_titles, new_figure, save, style_marker


def plot_nolan_index(path: str = None) -> str:
    fig, ax = new_figure()
    add_titles(fig, "The Nolan Index",
              "Syuzhet Craziness (the telling) vs. Fabula Craziness (the events)")

    for film in ALL_FILMS:
        fabula, syuzhet = NOLAN_INDEX[film]
        style_marker(ax, [fabula], [syuzhet])
        right_edge = fabula >= 9
        ax.annotate(FILM_LABELS[film].split(" (")[0], (fabula, syuzhet),
                   textcoords="offset points", xytext=(-8, 7) if right_edge else (8, 7),
                   ha="right" if right_edge else "left", fontsize=9,
                   fontfamily="Georgia", color=INK)

    ax.scatter([ODYSSEY_DEFAULT["fabula"]], [ODYSSEY_DEFAULT["syuzhet"]],
              marker="*", s=260, color=GOLD, edgecolors="#8a6a0e", zorder=4)
    ax.annotate("The Odyssey?", (ODYSSEY_DEFAULT["fabula"], ODYSSEY_DEFAULT["syuzhet"]),
               textcoords="offset points", xytext=(10, -14), fontsize=9,
               style="italic", fontfamily="Georgia")

    ax.set_xlabel("Fabula Craziness ->", fontfamily="Georgia", fontweight="bold", color="#1d6d47")
    ax.set_ylabel("Syuzhet Craziness ->", fontfamily="Georgia", fontweight="bold", color="#1d6d47")

    path = path or os.path.join(OUTPUT_DIR, "nolan_index.png")
    save(fig, path)
    return path
