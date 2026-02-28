import json
from pathlib import Path

import pytest

from app.infra.io_points import load_points_from_path, parse_points_bytes


def test_parse_txt_ok():
    content = b"0 0\n1,2\n# comment\n 3 4 \n"
    pts = parse_points_bytes("a.txt", content)
    assert len(pts) == 3
    assert (pts[1].x, pts[1].y) == (1.0, 2.0)


def test_parse_txt_bad_line():
    with pytest.raises(ValueError):
        parse_points_bytes("a.txt", b"0 0 0\n")


def test_parse_json_ok_list():
    payload = json.dumps([[0, 0], [1, 2]]).encode()
    pts = parse_points_bytes("a.json", payload)
    assert len(pts) == 2


def test_parse_json_ok_object_points():
    payload = json.dumps({"points": [{"x": 0, "y": 0}, {"x": 1, "y": 2}]}).encode()
    pts = parse_points_bytes("a.json", payload)
    assert len(pts) == 2


def test_load_points_from_folder_mixed(tmp_path: Path):
    (tmp_path / "a.txt").write_text("0 0\n1 1\n", encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps([[2, 2]]), encoding="utf-8")
    res = load_points_from_path(tmp_path)
    assert len(res.points) == 3
    assert len(res.sources) == 2
