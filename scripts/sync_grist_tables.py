#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from grist_inventory.common import (
    CUT_LIST_PATH,
    INVENTORY_PATH,
    MATERIAL_RULES_PATH,
    ROOT_DIR,
    SCHEMA_PATH,
    SHOPPING_LIST_PATH,
    load_snapshot,
    preserve_fields_by_key,
    read_json,
    write_snapshot,
)
from grist_inventory.grist_api import GristApiError, GristClient

load_dotenv(ROOT_DIR / ".env")


# Per-table sync registry.
#
# `direction` is the authoritative direction for a given table:
#   - "push": repo snapshot -> Grist (local is source of truth)
#   - "pull": Grist -> repo snapshot (Grist is source of truth)
#
# `preserve_fields` only applies to push and lists fields that are authored in Grist
# and must be carried across regeneration (e.g. the `completed` checkbox on cut_list).
TABLE_SPEC: dict[str, dict[str, Any]] = {
    "cut_list": {
        "direction": "push",
        "path": CUT_LIST_PATH,
        "primary_key": "cut_id",
        "preserve_fields": ["completed"],
    },
    "shopping_list": {
        "direction": "push",
        "path": SHOPPING_LIST_PATH,
        "primary_key": "shopping_id",
        "preserve_fields": [],
    },
    "inventory": {
        "direction": "pull",
        "path": INVENTORY_PATH,
        "primary_key": "inventory_id",
    },
    "material_rules": {
        "direction": "pull",
        "path": MATERIAL_RULES_PATH,
        "primary_key": "rule_id",
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


def push_table(client: GristClient, table_name: str) -> None:
    spec = TABLE_SPEC[table_name]
    path: Path = spec["path"]
    primary_key: str = spec["primary_key"]
    preserve_fields: list[str] = spec["preserve_fields"]

    snapshot = load_snapshot(path, table_name, primary_key)
    rows: list[dict[str, Any]] = list(snapshot["rows"])

    if preserve_fields:
        existing_rows = [
            dict(record.get("fields", {})) for record in client.fetch_records(table_name)
        ]
        rows = preserve_fields_by_key(
            rows=rows,
            existing_rows=existing_rows,
            primary_key=primary_key,
            editable_fields=preserve_fields,
        )
        write_snapshot(path, table_name, primary_key, rows)

    result = client.replace_records(table_name, primary_key, rows)
    print(
        f"Pushed {table_name}: upserted {result['upserted']} rows, deleted {result['deleted']} rows"
    )


def pull_table(client: GristClient, table_name: str) -> None:
    spec = TABLE_SPEC[table_name]
    path: Path = spec["path"]
    primary_key: str = spec["primary_key"]

    records = client.fetch_records(table_name)
    rows: list[dict[str, Any]] = []
    for record in records:
        fields = dict(record.get("fields", {}))
        if primary_key not in fields and "id" in record:
            fields[primary_key] = record["id"]
        rows.append(fields)
    write_snapshot(path, table_name, primary_key, rows)
    print(f"Pulled {table_name}: wrote {len(rows)} rows to {path}")


def sync_table(client: GristClient, table_name: str) -> None:
    spec = TABLE_SPEC[table_name]
    direction = spec["direction"]
    if direction == "push":
        push_table(client, table_name)
    elif direction == "pull":
        pull_table(client, table_name)
    else:
        raise SystemExit(
            f"Unknown sync direction '{direction}' for table '{table_name}'"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Sync Grist tables. With no --table flags, syncs all registered tables in "
            "their default directions (cut_list/shopping_list push, inventory/material_rules pull)."
        )
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
        help="Create missing tables and columns from data/grist_schema.json (one-time setup).",
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
        if args.bootstrap_schema:
            bootstrap_schema(client, SCHEMA_PATH)
            return 0

        tables_to_sync = args.table if args.table else list(TABLE_SPEC.keys())
        for table_name in tables_to_sync:
            sync_table(client, table_name)
    except GristApiError as exc:
        raise SystemExit(str(exc)) from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
