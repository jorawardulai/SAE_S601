from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

from app.domain.geometry import Point, unique_points


@dataclass(frozen=True, slots=True)
class ParseResult:
    points: List[Point]
    sources: List[str]  # filenames loaded


def _parse_txt(content: str) -> List[Point]:
    pts: List[Point] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.replace(",", " ")
        parts = [p for p in line.split() if p]
        if len(parts) != 2:
            raise ValueError(f"Invalid TXT line (expected 2 numbers): {raw!r}")
        x = float(parts[0])
        y = float(parts[1])
        pts.append(Point(x, y))
    return pts


def _parse_json(content: str) -> List[Point]:
    data = json.loads(content)
    pts: List[Point] = []

    def add_xy(x: object, y: object) -> None:
        pts.append(Point(float(x), float(y)))

    if isinstance(data, dict) and "points" in data:
        data = data["points"]

    if isinstance(data, list):
        for item in data:
            if isinstance(item, list) and len(item) == 2:
                add_xy(item[0], item[1])
            elif isinstance(item, dict) and "x" in item and "y" in item:
                add_xy(item["x"], item["y"])
            else:
                raise ValueError("Invalid JSON points format.")
        return pts

    raise ValueError("Invalid JSON: expected list or object with 'points' list.")


def parse_points_bytes(filename: str, content: bytes) -> List[Point]:
    name = filename.lower()
    text = content.decode("utf-8", errors="replace")
    if name.endswith(".txt"):
        return _parse_txt(text)
    if name.endswith(".json"):
        return _parse_json(text)
    raise ValueError("Unsupported file format (expected .txt or .json).")


def load_points_from_path(path: Union[str, Path]) -> ParseResult:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")

    if p.is_file():
        files = [p]
    else:
        files = sorted([f for f in p.rglob("*") if f.is_file() and f.suffix.lower() in {".txt", ".json"}])

    if not files:
        raise ValueError("No .txt or .json files found in the given path.")

    all_pts: List[Point] = []
    sources: List[str] = []
    for f in files:
        pts = parse_points_bytes(f.name, f.read_bytes())
        all_pts.extend(pts)
        sources.append(str(f))

    all_pts = unique_points(all_pts)
    return ParseResult(points=all_pts, sources=sources)
