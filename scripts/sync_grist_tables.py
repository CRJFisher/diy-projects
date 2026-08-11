#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from grist.common import (
    INVENTORY_PATH,
    ROOT_DIR,
    SCHEMA_PATH,
    load_snapshot,
    preserve_fields_by_key,
    read_json,
    write_snapshot,
)
from grist.grist_api import GristApiError, GristClient
from grist.project import (
    denamespace_pk,
    load_project,
    namespace_pk,
    row_belongs_to_project,
)


def _load_dotenv(path: Path) -> None:
    """Load KEY=VALUE pairs from ``path`` into ``os.environ`` if the file exists.

    Existing environment variables win (``setdefault``), matching python-dotenv's
    default behaviour for undeclared keys.
    """
    if not path.is_file():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


_load_dotenv(ROOT_DIR / ".env")


# Per-table sync registry (paths resolved per invocation for project-scoped tables).
#
# `direction` is the authoritative direction for a given table:
#   - "push": repo snapshot -> Grist (local is source of truth)
#   - "pull": Grist -> repo snapshot (Grist is source of truth)
#
# `scoped` means rows are filtered / namespaced by project_id.
TABLE_SPEC: dict[str, dict[str, Any]] = {
    "cut_list": {
        "direction": "push",
        "scoped": True,
        "primary_key": "cut_id",
        "preserve_fields": ["completed"],
        "reset_preserve_on_change": [
            "length_mm",
            "width_mm",
            "thickness_mm",
            "section_key",
            "qty_required",
        ],
    },
    "shopping_list": {
        "direction": "push",
        "scoped": True,
        "primary_key": "shopping_id",
        "preserve_fields": ["acquired"],
        "reset_preserve_on_change": [],
    },
    "inventory": {
        "direction": "pull",
        "scoped": False,
        "path": INVENTORY_PATH,
        "primary_key": "inventory_id",
    },
}


def build_client(args: argparse.Namespace) -> GristClient:
    api_key = args.api_key or os.environ.get("GRIST_API_KEY")
    doc_id = args.doc_id or os.environ.get("GRIST_DOC_ID")
    base_url = args.base_url or os.environ.get(
        "GRIST_BASE_URL", "https://docs.getgrist.com/api"
    )
    if not api_key or not doc_id:
        raise SystemExit(
            "Missing Grist credentials. Set GRIST_API_KEY and GRIST_DOC_ID or pass --api-key/--doc-id."
        )
    return GristClient(api_key=api_key, doc_id=doc_id, base_url=base_url)


def bootstrap_schema(client: GristClient, schema_path: Path) -> None:
    schema = read_json(schema_path, default={"tables": []})
    existing_lower = {tid.lower() for tid in client.list_tables()}
    for table_spec in schema["tables"]:
        requested_id = table_spec["id"]
        if requested_id.lower() not in existing_lower:
            assigned_id = client.create_table(table_spec)
            if assigned_id.lower() != requested_id.lower():
                print(
                    f"Warning: Grist stored table as '{assigned_id}' (schema requested '{requested_id}')."
                )
            print(f"Created table: {assigned_id}")
        client.ensure_columns(table_spec)
        print(f"Ensured columns for table: {table_spec['id']}")


def _project_path(project: Any, table_name: str) -> Path:
    if table_name == "cut_list":
        return project.cut_list_path
    if table_name == "shopping_list":
        return project.shopping_list_path
    raise SystemExit(f"No project-local path for table {table_name!r}")


def _to_grist_rows(
    project_id: str,
    primary_key: str,
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grist_rows: list[dict[str, Any]] = []
    for row in rows:
        grist_row = dict(row)
        local_id = str(grist_row.get(primary_key, ""))
        grist_row["project_id"] = project_id
        grist_row[primary_key] = namespace_pk(project_id, local_id)
        grist_rows.append(grist_row)
    return grist_rows


def _from_grist_rows(
    project_id: str,
    primary_key: str,
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    local_rows: list[dict[str, Any]] = []
    for row in rows:
        if not row_belongs_to_project(row, project_id, primary_key):
            # Legacy rows: no project_id and un-namespaced key — treat as this
            # project only when the key has no namespace separator.
            if row.get("project_id"):
                continue
            key = str(row.get(primary_key, ""))
            if "__" in key:
                continue
        local_row = dict(row)
        key = str(local_row.get(primary_key, ""))
        local_row[primary_key] = denamespace_pk(project_id, key)
        local_row.pop("project_id", None)
        local_rows.append(local_row)
    return local_rows


def _delete_predicate(
    project_id: str,
    primary_key: str,
    local_short_keys: set[str],
) -> Callable[[dict[str, Any]], bool]:
    def predicate(fields: dict[str, Any]) -> bool:
        if row_belongs_to_project(fields, project_id, primary_key):
            return True
        # Legacy unscoped rows whose bare key matches this project's local ids.
        if not fields.get("project_id"):
            key = fields.get(primary_key)
            if isinstance(key, str) and key in local_short_keys and "__" not in key:
                return True
        return False

    return predicate


def push_table(client: GristClient, table_name: str, project: Any) -> None:
    spec = TABLE_SPEC[table_name]
    primary_key: str = spec["primary_key"]
    preserve_fields: list[str] = spec.get("preserve_fields") or []
    reset_on_change: list[str] = spec.get("reset_preserve_on_change") or []
    path = _project_path(project, table_name)
    project_id = project.slug

    snapshot = load_snapshot(path, table_name, primary_key)
    rows: list[dict[str, Any]] = list(snapshot["rows"])
    local_short_keys = {
        str(row.get(primary_key, ""))
        for row in rows
        if row.get(primary_key) not in (None, "")
    }

    if preserve_fields:
        existing_records = client.fetch_records(table_name)
        existing_local = _from_grist_rows(
            project_id,
            primary_key,
            [dict(record.get("fields", {})) for record in existing_records],
        )
        rows = preserve_fields_by_key(
            rows=rows,
            existing_rows=existing_local,
            primary_key=primary_key,
            editable_fields=preserve_fields,
            reset_on_change_fields=reset_on_change,
        )
        write_snapshot(path, table_name, primary_key, rows)

    grist_rows = _to_grist_rows(project_id, primary_key, rows)
    result = client.replace_records(
        table_name,
        primary_key,
        grist_rows,
        delete_predicate=_delete_predicate(project_id, primary_key, local_short_keys),
    )
    print(
        f"Pushed {table_name} ({project_id}): upserted {result['upserted']} rows, "
        f"deleted {result['deleted']} rows"
    )


def pull_table(
    client: GristClient,
    table_name: str,
    project: Any | None = None,
) -> None:
    spec = TABLE_SPEC[table_name]
    primary_key: str = spec["primary_key"]
    scoped = bool(spec.get("scoped"))

    if scoped:
        if project is None:
            raise SystemExit(f"--project is required to pull scoped table {table_name}")
        path = _project_path(project, table_name)
    else:
        path = Path(spec["path"])

    records = client.fetch_records(table_name)
    rows: list[dict[str, Any]] = []
    for record in records:
        fields = dict(record.get("fields", {}))
        if primary_key not in fields and "id" in record:
            fields[primary_key] = record["id"]
        rows.append(fields)

    if scoped and project is not None:
        rows = _from_grist_rows(project.slug, primary_key, rows)

    write_snapshot(path, table_name, primary_key, rows)
    print(f"Pulled {table_name}: wrote {len(rows)} rows to {path}")


def sync_table(
    client: GristClient,
    table_name: str,
    project: Any | None,
) -> None:
    spec = TABLE_SPEC[table_name]
    direction = spec["direction"]
    scoped = bool(spec.get("scoped"))
    if scoped and project is None:
        raise SystemExit(f"--project is required to sync scoped table {table_name}")
    if direction == "push":
        push_table(client, table_name, project)
    elif direction == "pull":
        pull_table(client, table_name, project if scoped else None)
    else:
        raise SystemExit(
            f"Unknown sync direction '{direction}' for table '{table_name}'"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync Grist tables for a DIY project. Project-scoped tables "
            "(cut_list, shopping_list) push local → Grist; shared inventory pulls "
            "Grist → shared/inventory/inventory.json."
        )
    )
    parser.add_argument(
        "--project",
        help="Project slug under projects/ (required unless only pulling inventory).",
    )
    parser.add_argument("--api-key", help="Grist API key. Defaults to GRIST_API_KEY.")
    parser.add_argument("--doc-id", help="Grist document id. Defaults to GRIST_DOC_ID.")
    parser.add_argument(
        "--base-url",
        help="Grist API base URL. Defaults to GRIST_BASE_URL or hosted Grist.",
    )
    parser.add_argument(
        "--bootstrap-schema",
        action="store_true",
        help="Create missing tables and columns from shared/schema/grist_schema.json.",
    )
    parser.add_argument(
        "--table",
        action="append",
        choices=sorted(TABLE_SPEC.keys()),
        help=(
            "Sync a specific table in its default direction. Repeat to sync multiple "
            "tables. Omit to sync all registered tables."
        ),
    )
    args = parser.parse_args()

    client = build_client(args)
    try:
        # Always run schema bootstrap first. It's idempotent (creates missing
        # tables and columns, leaves existing ones alone), so a schema change
        # in shared/schema/grist_schema.json is automatically reflected on the
        # next sync without the user needing to remember --bootstrap-schema.
        bootstrap_schema(client, SCHEMA_PATH)
        if args.bootstrap_schema and args.table is None and not args.project:
            return 0

        tables_to_sync = args.table if args.table else list(TABLE_SPEC.keys())
        needs_project = any(TABLE_SPEC[name].get("scoped") for name in tables_to_sync)
        if needs_project and not args.project:
            raise SystemExit(
                "--project is required when syncing cut_list or shopping_list."
            )

        project = load_project(args.project) if args.project else None
        for table_name in tables_to_sync:
            sync_table(client, table_name, project)
    except GristApiError as exc:
        raise SystemExit(str(exc)) from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
