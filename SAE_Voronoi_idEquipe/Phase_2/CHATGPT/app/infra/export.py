from __future__ import annotations

from io import BytesIO

import matplotlib.pyplot as plt


def figure_to_png_bytes(fig: plt.Figure, dpi: int = 200) -> bytes:
    bio = BytesIO()
    fig.savefig(bio, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0)
    return bio.getvalue()


def figure_to_svg_bytes(fig: plt.Figure) -> bytes:
    bio = BytesIO()
    fig.savefig(bio, format="svg", bbox_inches="tight", pad_inches=0)
    return bio.getvalue()
