---
name: build-store-adapter
description: Reverse-engineer an ecommerce site's search and emit a deterministic adapter script under scripts/store_adapters/<slug>/.
disable-model-invocation: true
argument-hint: "[site-url]"
allowed-tools:
  [
    Bash(cd tooling/adapter-builder && npm install*),
    Bash(cd tooling/adapter-builder && npm run record*),
    Bash(cd scripts/store_adapters/* && npm install*),
    Bash(cd scripts/store_adapters/* && npm test*),
    Bash(cd scripts/store_adapters/* && npm run typecheck*),
    Bash(cd scripts/store_adapters/* && npx playwright install*),
    Bash(npx --prefix scripts/store_adapters/* tsx*),
    Bash(find scripts/store_adapters/*),
    Read,
    Write,
    Edit,
    Task,
    AskUserQuestion,
  ]
---

# build-store-adapter

Builds a per-site ecommerce search adapter. The runtime adapter does not call any LLM — analysis cost is paid once during this skill run, then every future search is a deterministic HTTP call (or a scoped browser run if the site can't be scraped without one).

## Layout

Three locations, one per role:

- `tooling/adapter-builder/` — bootstrap recorder. One copy, hand-authored. Drives Stagehand + Playwright, writes `recordings.json`.
- `scripts/store_adapters/<slug>/` — one generated adapter per site. Contains `search.ts`, `search.test.ts`, `manifest.json`, `recordings.json`, `package.json`, `tsconfig.json`.
- `.claude/skills/build-store-adapter/` — this skill, orchestrating the two.

## Preconditions

- **Working directory:** repo root (`/Users/chuck/workspace/diy-projects`).
- **Env var:** `OPENROUTER_API_KEY` must be set. The recorder loads it via `node --env-file-if-exists=../../.env`, so the canonical place is the repo-root `.env` (alongside the existing Grist keys; see `.env.sample`). A shell-exported variable also works. If neither source provides it, stop and name the variable.
- **Node toolchain:** `node` ≥ 20.12 and `npm` on PATH (the recorder's npm script uses `--env-file-if-exists`, added in 20.12).
- **Bootstrap workspace:** `tooling/adapter-builder/`. The skill installs deps on first use.
- **Single concurrent run.** Stagehand `LOCAL` launches Chromium on a local CDP port; two parallel skill invocations collide. Run one at a time.

## Workflow

### Phase 1 — Gather inputs

The user may pass a site URL as the slash-command argument:

```
ARGUMENTS: $ARGUMENTS
```

- If `$ARGUMENTS` above is non-empty, treat its first whitespace-trimmed token as the **target site URL** and skip the URL question.
- If `$ARGUMENTS` is empty, ask for the URL.

Then ask via a single `AskUserQuestion` call (omit the URL question when supplied as an argument):

1. **Target site URL** (only if not provided as `$ARGUMENTS`) — e.g. `https://www.diy.com`.
2. **Sample search queries** — 3 to 5 strings that each return non-empty results on the target site. These drive both the analysis and the golden test.
3. **Output slug** — directory name under `scripts/store_adapters/`. Default rule: lowercase the host, replace dots with underscores, strip a leading `www_`. Examples: `www.diy.com` → `diy_com`; `shop.acme.co.uk` → `shop_acme_co_uk`.

Verify `OPENROUTER_API_KEY` is set. Stop with the variable name if not.

If `scripts/store_adapters/<slug>/` already exists, ask the user via a second `AskUserQuestion`:

- **Overwrite** — refresh the adapter, keep the slug. Continue.
- **Bump suffix** — auto-suffix `_v2`, `_v3` etc. Continue with the new slug.
- **Abort** — stop the skill.

If `tooling/adapter-builder/node_modules/` does not exist:

```bash
cd tooling/adapter-builder && npm install
```

### Phase 2 — Record

Run the recorder for all queries. Pass `--out` as an absolute path so it lands directly in the adapter dir without a copy step:

```bash
cd tooling/adapter-builder && npm run record -- \
  --site "https://www.diy.com" \
  --queries '["CLS timber 50x47","plywood exterior 18mm"]' \
  --out "/Users/chuck/workspace/diy-projects/scripts/store_adapters/diy_com"
```

Substitute the user-supplied site URL, the JSON-encoded queries array, and the slug from Phase 1.

The recorder is interactive — Chromium opens locally. Wait for it to finish; do not background it. It writes `recordings.json` after every query, so even a partial run produces a usable file.

If the recorder errors on a query with "produced no visible product cards", the file still has earlier queries. Read the file, count `queries[i].error` entries, and:

- If every query errored: the user's queries don't return organic results on the site (or the site is showing a captcha / location prompt). Show the page snippet from the first error and ask the user to revise the queries or supply a postcode/location upfront.
- If some queries succeeded: continue to Phase 3 with what was captured. Note the failure count in the final report.

After the recorder returns, sanity-check by reading the first successful query's product titles aloud to the user (one line: "captured N products for query X — looks like real product results: titles A, B, C").

### Phase 3 — Analyze and generate

Spawn the project-scoped `store-adapter-generator` subagent (defined in `.claude/agents/store-adapter-generator.md`) via the Task tool. Pass `subagent_type: "store-adapter-generator"`.

The agent reads the recording, classifies the site, and writes the adapter files. It does not run any of them — that's Phase 4.

The agent's full system prompt and output contract live in its definition file; do not duplicate them here. The skill's job in this phase is just to invoke the agent with the two paths and capture the JSON summary it returns.

**Task prompt** (the entire user-message to the agent):

```text
RECORDING_PATH: <absolute path to recordings.json from Phase 2>
OUTPUT_DIR: <absolute path to scripts/store_adapters/<slug>/>
```

The agent returns a single JSON object on stdout:

```jsonc
{
  "method": "json_api" | "html_embedded_json" | "browser_required",
  "endpoint_url": "https://...",          // null for browser_required
  "selected_candidate_url": "https://...", // the network candidate that won the cross-reference
  "files_written": [/* paths under OUTPUT_DIR */],
  "per_query_overlap": [{ "query": "...", "overlap": 0.83 }]
}
```

Parse it; carry `files_written` and `per_query_overlap` into Phase 3.5 and Phase 5.

### Phase 3.5 — Verify subagent output

Before running anything, confirm the subagent wrote what it claimed:

- Read each path in `files_written`. The set must include `manifest.json`, `package.json`, `tsconfig.json`, `search.ts`, `search.test.ts`, and `recordings.json`.
- Validate `manifest.json` parses and contains `method`, `field_map`, `validation`.
- If any file is missing or `manifest.json` is malformed, treat as a regeneration failure (see Phase 4).

### Phase 4 — Validate

Run in sequence; stop on first failure:

```bash
cd scripts/store_adapters/<slug> && npm install
cd scripts/store_adapters/<slug> && npm run typecheck
```

If `method == "browser_required"`, install Chromium for the adapter's `node_modules`:

```bash
cd scripts/store_adapters/<slug> && npx playwright install chromium
```

Then:

```bash
cd scripts/store_adapters/<slug> && npm test
```

**On typecheck or test failure**, retry the subagent **at most once**. Build the retry prompt by appending this block to the original Phase 3 prompt:

```text
The previous generation produced these errors. Fix them and re-emit only the changed files. Errors:

<paste tsc/vitest output verbatim>
```

If still failing after one retry, stop and ask the user via `AskUserQuestion`:

- **Force a different method** — re-run Phase 3 with the prompt amended to "skip method `<failed>` and choose between `<remaining>`".
- **Re-record with new queries** — return to Phase 2.
- **Stop and report** — leave files in place; set `manifest.validation.passed: false`.

**On all tests passing**, edit `manifest.json` to set `validation.passed: true`, then run a final smoke test:

```bash
cd scripts/store_adapters/<slug> && npx tsx search.ts "<first sample query>" --max 5
```

Confirm stdout is a JSON object with a non-empty `products` array, each with at least `title` and `url`.

### Phase 5 — Report

Render this template literally, filling in the bracketed values:

```text
Built {method} adapter for {site}.
Endpoint: {endpoint_url or "n/a (browser_required)"}
Validation: {N}/{M} queries passed at ≥0.5 title overlap (per-query: q1=0.83, q2=0.71, ...).
Path: scripts/store_adapters/{slug}/
Usage: npx tsx scripts/store_adapters/{slug}/search.ts "<query>" --max 10
```

Then a single trailing sentence: "Wiring callers to this adapter is a separate task."

## Cowork notes

This skill is interactive — Phase 1 uses `AskUserQuestion` and Phase 2 opens a visible Chromium window. It is not safe to run via Cowork's headless proxy. If invoked from a headless context, stop after the precondition check and report: "build-store-adapter requires an interactive session; rerun in Claude Code CLI on the user's machine."

## Error handling

- **`OPENROUTER_API_KEY` unset** — stop in Phase 1, name the variable.
- **`npm install` in `tooling/adapter-builder/` fails** — show the npm error verbatim and stop. Common causes: no network, npm registry config, Node version too old.
- **Recorder cannot find search input** (Stagehand `act` returns "could not locate") — the site likely uses a non-standard search trigger or hides search behind a region/postcode prompt. Stop and ask the user for a direct search-results URL pattern (`?q={query}`) they want to use instead — the analyzer can sometimes work from that alone.
- **Visible products extracted but no JSON candidate scores ≥60% on more than one query** — the legitimate `browser_required` case. The subagent picks that method automatically.
- **Adapter typechecks and tests pass but `npx tsx search.ts` returns an empty products list at the smoke-test step** — a session-bound header in the manifest has expired. Re-run the skill with the same site and queries to capture fresh headers; the regenerated manifest replaces the stale one.

## Out of scope

- Pagination beyond the first results page. The adapter returns the first page; if the user needs more, that's a follow-up.
- Login-gated search. The recorder runs an unauthenticated session; sites that hide search behind a login are out of scope.
- Region/postcode gates. If the site requires a postcode prompt, prices and stock state will be missing from the recording. The user can supply a postcode via the search query or work with what's captured.
- Auto-rewiring callers (e.g. `bin-store-shopping`) to use the generated adapter — separate task.
- Generating adapters in any language other than TypeScript.
