"""Shared chart style, so every plot this project makes reads as one system.

Palette mirrors css/theme.css and js/graph.js::ratingColor exactly, so a
static chart and the live website feel like the same publication.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

BG       = "#f5f5f5"
PANEL_BG = "#f0f0f0"

GREEN_DARK  = "#1d6d47"
GREEN_MID   = "#2a8f5e"
GREEN_LIGHT = "#89dd9d"
RUST        = "#c4694d"
RUST_DARK   = "#a3502e"
GOLD        = "#d4a017"
GRID        = "#d8d8d8"
BORDER      = "#cccccc"
INK         = "#1a1a1a"

FONT_SERIF = "Liberation Serif"


def new_figure(figsize: tuple = (11, 7)):
    """A blank chart in the house style, with room reserved for a title block."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG)
    fig.subplots_adjust(top=0.84, left=0.09, right=0.97, bottom=0.12)

    ax.set_facecolor(PANEL_BG)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.7, color=GRID, alpha=0.9)
    ax.xaxis.grid(True, linestyle="--", linewidth=0.7, color=GRID, alpha=0.9)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(1.0)

    ax.tick_params(colors="#555555", labelsize=12.5)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(FONT_SERIF)
        label.set_color("#555555")

    return fig, ax


def add_titles(fig, title: str, subtitle: str):
    """Bold-uppercase title + green italic subtitle + rule below subtitle."""
    fig.text(0.048, 0.97, title.upper(),
             fontsize=19, fontweight="bold",
             fontfamily=FONT_SERIF, color=INK, ha="left", va="top")

    sub = fig.text(0.048, 0.91, subtitle,
                   fontsize=13.5, fontfamily=FONT_SERIF,
                   color=GREEN_DARK, ha="left", va="top", style="italic")

    # Draw accent rule dynamically just below the subtitle text
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox     = sub.get_window_extent(renderer=renderer)
    bbox_fig = bbox.transformed(fig.transFigure.inverted())
    line_y   = bbox_fig.y0 - 0.012

    fig.add_artist(plt.Line2D([0.048, 0.95], [line_y, line_y],
                              transform=fig.transFigure,
                              color=BORDER, linewidth=0.8))


def set_axis_labels(ax, xlabel: str, ylabel: str):
    """Bold serif axis labels in dark green."""
    ax.set_xlabel(xlabel, fontsize=13.5, fontweight="bold",
                  color=GREEN_DARK, labelpad=16, fontfamily=FONT_SERIF)
    ax.set_ylabel(ylabel, fontsize=13.5, fontweight="bold",
                  color=GREEN_DARK, labelpad=10, fontfamily=FONT_SERIF)


def style_marker(ax, x, y, **kwargs):
    """Double-tone ring + centre dot marker in green-light."""
    ax.scatter(x, y, s=120, color=PANEL_BG, edgecolors=GREEN_LIGHT,
               linewidths=1.8, zorder=5)
    defaults = dict(s=30, color=GREEN_LIGHT, zorder=6)
    defaults.update(kwargs)
    return ax.scatter(x, y, **defaults)


def annotate_point(ax, x, y, text, ha="left", va="bottom", dx=8, dy=6):
    """Film-label annotation with a background stroke to lift it off the panel."""
    ax.annotate(
        text, (x, y),
        textcoords="offset points", xytext=(dx, dy),
        fontsize=12.5, color=GREEN_DARK, fontfamily=FONT_SERIF,
        ha=ha, va=va,
        path_effects=[pe.withStroke(linewidth=2.5, foreground=PANEL_BG)],
    )


def fit_line(ax, x, y, color: str = RUST, label: str = None, **kwargs):
    """A fit curve with the three-pass soft glow effect, then the main line."""
    for lw, alpha in [(10, 0.08), (6, 0.13), (3, 0.22)]:
        ax.plot(x, y, color=color, linewidth=lw, alpha=alpha, zorder=2)
    defaults = dict(color=color, linewidth=1.6, zorder=3)
    if label:
        defaults["label"] = label
    defaults.update(kwargs)
    return ax.plot(x, y, **defaults)


def equation_box(ax, text: str):
    """Small italic caption describing the fit, boxed to match the panel."""
    return ax.text(0.03, 0.95, text, transform=ax.transAxes,
                   fontsize=11, style="italic", fontfamily=FONT_SERIF,
                   color=INK, ha="left", va="top",
                   bbox=dict(boxstyle="round,pad=0.45", facecolor=BG,
                             edgecolor=BORDER, alpha=0.9))


def add_legend(ax):
    """Legend styled to match the panel."""
    leg = ax.legend(fontsize=11.5, loc="lower left",
                    facecolor=BG, edgecolor=BORDER,
                    labelcolor=RUST, framealpha=0.9)
    for text in leg.get_texts():
        text.set_fontfamily(FONT_SERIF)
    return leg


def save(fig, path: str, dpi: int = 180):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
