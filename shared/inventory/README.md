# Shared workshop inventory

Repo snapshot of the Grist `inventory` table (pull-only). Edited in Grist; pulled by:

```bash
python3 scripts/sync_grist_tables.py --project <any-slug> --table inventory
```

(or a full project sync). All projects share this stock. Shopping computation reserves inventory for other projects' incomplete cuts before calculating the active project's shortfall.
