from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class GristApiError(RuntimeError):
    """Raised when the Grist API returns an error."""


class GristClient:
    def __init__(self, api_key: str, doc_id: str, base_url: str) -> None:
        self.api_key = api_key
        self.doc_id = doc_id
        self.base_url = base_url.rstrip("/")
        self._table_id_by_lower: dict[str, str] = {}
        self._table_cache_loaded = False

    def list_tables(self) -> list[str]:
        payload = self._request_json("GET", f"/docs/{self.doc_id}/tables")
        table_ids = [table["id"] for table in payload.get("tables", [])]
        self._table_id_by_lower = {tid.lower(): tid for tid in table_ids}
        self._table_cache_loaded = True
        return table_ids

    def _resolve_table_id(self, requested_id: str) -> str:
        """Map the caller's schema id to the id Grist actually stored.

        Grist normalizes table ids to valid Python identifiers (capitalizes the
        first letter), so a schema with `cut_list` is stored as `Cut_list` and
        must be addressed that way in subsequent URLs.
        """
        if not self._table_cache_loaded:
            self.list_tables()
        return self._table_id_by_lower.get(requested_id.lower(), requested_id)

    def create_table(self, table_spec: dict[str, Any]) -> str:
        body = {
            "tables": [
                {
                    "id": table_spec["id"],
                    "columns": [
                        {
                            "id": column["id"],
                            "fields": {
                                "label": column.get("label", column["id"]),
                                "type": column.get("type", "Text"),
                            },
                        }
                        for column in table_spec["columns"]
                    ],
                }
            ]
        }
        response = self._request_json("POST", f"/docs/{self.doc_id}/tables", body)
        created = response.get("tables", [])
        if not created or "id" not in created[0]:
            raise GristApiError(
                f"Unexpected response creating table {table_spec['id']!r}: {response}"
            )
        assigned_id = created[0]["id"]
        self._table_id_by_lower[assigned_id.lower()] = assigned_id
        return assigned_id

    def ensure_columns(self, table_spec: dict[str, Any]) -> None:
        table_id = self._resolve_table_id(table_spec["id"])
        body = {
            "columns": [
                {
                    "id": column["id"],
                    "fields": {
                        "label": column.get("label", column["id"]),
                        "type": column.get("type", "Text"),
                    },
                }
                for column in table_spec["columns"]
            ]
        }
        self._request_json(
            "PUT",
            f"/docs/{self.doc_id}/tables/{urllib.parse.quote(table_id)}/columns",
            body,
        )
        self.normalize_column_ids(table_spec)

    def normalize_column_ids(self, table_spec: dict[str, Any]) -> list[list[Any]]:
        """Rename any Grist-normalized column ids back to the schema's snake_case.

        Grist derives column ids from the column `label` (`"Cut ID"` →
        `Cut_ID`, `"Length (mm)"` → `Length_mm_`), ignoring the `id` we send on
        create. This method diffs the stored column ids against the schema and
        emits `RenameColumn` actions for any mismatch, and `RemoveColumn` for
        stored columns the schema no longer lists. Matching is by lowercase id
        with trailing underscores stripped.
        """
        table_id = self._resolve_table_id(table_spec["id"])
        payload = self._request_json(
            "GET", f"/docs/{self.doc_id}/tables/{urllib.parse.quote(table_id)}/columns"
        )
        current_ids = [col["id"] for col in payload.get("columns", [])]
        desired_ids = [col["id"] for col in table_spec["columns"]]

        def norm(value: str) -> str:
            return value.lower().rstrip("_")

        desired_by_norm = {norm(d): d for d in desired_ids}
        actions: list[list[Any]] = []
        matched: set[str] = set()
        for current in current_ids:
            want = desired_by_norm.get(norm(current))
            if want is None:
                actions.append(["RemoveColumn", table_id, current])
            elif current != want:
                actions.append(["RenameColumn", table_id, current, want])
                matched.add(current)
            else:
                matched.add(current)
        if actions:
            self._request_json("POST", f"/docs/{self.doc_id}/apply", actions)
        return actions

    def fetch_records(self, table_id: str) -> list[dict[str, Any]]:
        resolved = self._resolve_table_id(table_id)
        payload = self._request_json(
            "GET",
            f"/docs/{self.doc_id}/tables/{urllib.parse.quote(resolved)}/records",
        )
        return payload.get("records", [])

    def upsert_records(
        self,
        table_id: str,
        primary_key: str,
        rows: list[dict[str, Any]],
    ) -> None:
        if not rows:
            return

        resolved = self._resolve_table_id(table_id)
        body = {
            "records": [
                {
                    "require": {primary_key: row[primary_key]},
                    "fields": row,
                }
                for row in rows
            ]
        }
        self._request_json(
            "PUT",
            f"/docs/{self.doc_id}/tables/{urllib.parse.quote(resolved)}/records",
            body,
            query={"onmany": "first"},
        )

    def delete_records(self, table_id: str, row_ids: list[int]) -> None:
        if not row_ids:
            return
        resolved = self._resolve_table_id(table_id)
        self._request_json(
            "POST",
            f"/docs/{self.doc_id}/tables/{urllib.parse.quote(resolved)}/records/delete",
            row_ids,
        )

    def replace_records(
        self,
        table_id: str,
        primary_key: str,
        rows: list[dict[str, Any]],
    ) -> dict[str, int]:
        existing_records = self.fetch_records(table_id)
        existing_by_key = {
            record.get("fields", {}).get(primary_key): record.get("id")
            for record in existing_records
            if record.get("fields", {}).get(primary_key) not in (None, "")
        }
        local_keys = {row[primary_key] for row in rows}
        delete_ids = [
            row_id
            for key, row_id in existing_by_key.items()
            if key not in local_keys and row_id is not None
        ]

        self.upsert_records(table_id, primary_key, rows)
        self.delete_records(table_id, delete_ids)
        return {"upserted": len(rows), "deleted": len(delete_ids)}

    def _request_json(
        self,
        method: str,
        path: str,
        body: Any = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        query_string = ""
        if query:
            query_string = "?" + urllib.parse.urlencode(query)
        url = f"{self.base_url}{path}{query_string}"

        data = None
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                payload = response.read()
                if not payload:
                    return {}
                return json.loads(payload)
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise GristApiError(f"{exc.code} {exc.reason}: {error_body}") from exc
