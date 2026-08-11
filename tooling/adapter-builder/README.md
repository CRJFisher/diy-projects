# adapter-builder

Records ecommerce search sessions so the `build-store-adapter` skill can generate a deterministic adapter script per site. Bootstrap-only — no runtime adapter depends on this workspace.

## How it works

1. Stagehand opens a Chromium browser locally and drives the page via `act()` and `extract()`.
2. Playwright connects to the same browser over CDP and listens to every XHR/fetch response, recording JSON bodies plus failed requests.
3. After each search settles (`networkidle` with a 15 s ceiling), Stagehand's `extract()` pulls the visible product cards out of the rendered DOM as ground truth.
4. All queries are written incrementally to a single `recordings.json`. Cross-referencing network candidates against visible products is what lets the analyzer subagent find the real search endpoint among the noise of analytics, autocomplete, and recommendation calls.

## Install

```bash
cd tooling/adapter-builder
npm install
```

`OPENROUTER_API_KEY` must be available when `npm run record` runs. The `record` script uses `node --env-file-if-exists=../../.env`, so the canonical place is the repo-root `.env` (alongside the existing `GRIST_*` keys — see `.env.sample`). A shell-exported variable also works. Stagehand's `act`/`extract` calls go through OpenRouter using the OpenAI-compatible protocol (default model: `moonshotai/kimi-k2.6`; override with `--model`).

Requires Node ≥ 20.12 (for `--env-file-if-exists`).

## Run

```bash
OPENROUTER_API_KEY=sk-or-... npm run record -- \
  --site "https://www.diy.com" \
  --queries '["CLS timber 50x47","featheredge cladding 125mm","plywood exterior 18mm"]' \
  --out /Users/chuck/workspace/diy-projects/shared/store_adapters/diy_com
```

Pass `--out` as an absolute path. When invoked by the `build-store-adapter` skill, `--out` points directly at `shared/store_adapters/<slug>/` so the analyzer subagent finds the recording without a copy step.

Output: `<out>/recordings.json`:

```jsonc
{
  "site": "https://www.diy.com",
  "captured_at": "2026-04-29T...",
  "queries": [
    {
      "query": "CLS timber 50x47",
      "final_url": "https://www.diy.com/...",
      "network_candidates": [/* JSON xhr/fetch responses */],
      "failed_requests": [/* xhr/fetch that errored */],
      "ground_truth_products": [/* visible product cards */],
    },
  ],
}
```

If a query fails, the corresponding `QueryRecording` carries an `error` string and the loop continues. The recorder writes `recordings.json` after every query, so a partial recording survives a crash.

## Layout

- `src/types.ts` — `Recording`, `QueryRecording`, `NetworkCandidate`, `FailedRequest`, `GroundTruthProduct` (Zod schema).
- `src/recorder.ts` — Stagehand+Playwright session, network capture, ground-truth extraction.
- `src/cli.ts` — `record` subcommand entry point.
