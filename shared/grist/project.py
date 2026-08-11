from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]


ROOT_DIR = Path(__file__).resolve().parents[2]
PROJECTS_DIR = ROOT_DIR / "projects"
SHARED_DIR = ROOT_DIR / "shared"
INVENTORY_PATH = SHARED_DIR / "inventory" / "inventory.json"
SCHEMA_PATH = SHARED_DIR / "schema" / "grist_schema.json"

PK_SEPARATOR = "__"


@dataclass(frozen=True)
class ProjectPaths:
    slug: str
    name: str
    root: Path
    parameters_path: Path
    cut_list_path: Path
    shopping_list_path: Path
    substitution_candidates_path: Path
    extraction_module: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"


def namespace_pk(project_id: str, local_id: str) -> str:
    """Build a Grist-global primary key from a project-local id."""
    if not local_id:
        return local_id
    if local_id.startswith(f"{project_id}{PK_SEPARATOR}"):
        return local_id
    return f"{project_id}{PK_SEPARATOR}{local_id}"


def denamespace_pk(project_id: str, namespaced_id: str) -> str:
    """Strip the project prefix from a Grist-global primary key."""
    prefix = f"{project_id}{PK_SEPARATOR}"
    if namespaced_id.startswith(prefix):
        return namespaced_id[len(prefix) :]
    return namespaced_id


def row_belongs_to_project(
    row: dict[str, Any],
    project_id: str,
    primary_key: str,
) -> bool:
    if row.get("project_id") == project_id:
        return True
    key = row.get(primary_key)
    return isinstance(key, str) and key.startswith(f"{project_id}{PK_SEPARATOR}")


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def list_project_slugs() -> list[str]:
    if not PROJECTS_DIR.is_dir():
        return []
    slugs: list[str] = []
    for child in sorted(PROJECTS_DIR.iterdir()):
        if child.is_dir() and (child / "project.toml").is_file():
            slugs.append(child.name)
    return slugs


def load_project(slug: str) -> ProjectPaths:
    root = PROJECTS_DIR / slug
    config_path = root / "project.toml"
    if not config_path.is_file():
        known = ", ".join(list_project_slugs()) or "(none)"
        raise SystemExit(
            f"Unknown project {slug!r}. Expected {config_path}. Known: {known}"
        )
    config = _load_toml(config_path)
    project_slug = str(config.get("slug") or slug)
    if project_slug != slug:
        raise SystemExit(
            f"project.toml slug {project_slug!r} does not match directory {slug!r}"
        )
    name = str(config.get("name") or slug)
    parameters_rel = str(config.get("parameters", "model/parameters.scad"))
    data_rel = str(config.get("data_dir", "data"))
    extraction_rel = str(config.get("extraction", "extraction.py"))
    data_dir = root / data_rel
    return ProjectPaths(
        slug=project_slug,
        name=name,
        root=root,
        parameters_path=root / parameters_rel,
        cut_list_path=data_dir / "cut_list.json",
        shopping_list_path=data_dir / "shopping_list.json",
        substitution_candidates_path=data_dir / "substitution_candidates.json",
        extraction_module=root / extraction_rel,
    )


def other_projects(slug: str) -> list[ProjectPaths]:
    return [load_project(other) for other in list_project_slugs() if other != slug]
