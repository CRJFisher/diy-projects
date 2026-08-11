from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_parameters(path: Path) -> dict[str, Any]:
    """Return parameters once `model/parameters.scad` exists; empty until then."""
    del path
    return {}


def build_cut_list_rows(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    del parameters
    return []
