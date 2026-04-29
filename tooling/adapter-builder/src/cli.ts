#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { record } from "./recorder.js";
import type { Recording } from "./types.js";

const DEFAULT_MODEL = "moonshotai/kimi-k2.6";

const STRING_FLAGS = new Set(["site", "queries", "out", "model"]);

function usage(exit_code = 1): never {
  console.error(
    "Usage: adapter-builder record --site <url> --queries <json-array> --out <dir> [--model <slug>]",
  );
  console.error("");
  console.error("  --site     Target site URL");
  console.error("  --queries  JSON array of search queries");
  console.error("  --out      Output directory (recordings.json is written here)");
  console.error(`  --model    OpenRouter model slug (default: ${DEFAULT_MODEL})`);
  process.exit(exit_code);
}

function parse_flags(argv: string[]): Record<string, string> {
  const flags: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a) continue;
    if (!a.startsWith("--")) {
      console.error(`unexpected positional argument: ${a}`);
      usage();
    }
    const key = a.slice(2);
    const next = argv[i + 1];
    if (STRING_FLAGS.has(key)) {
      if (next === undefined || next.startsWith("--")) {
        console.error(`flag --${key} requires a value`);
        usage();
      }
      flags[key] = next;
      i++;
    } else {
      flags[key] = "true";
    }
  }
  return flags;
}

async function main(): Promise<void> {
  const [cmd, ...rest] = process.argv.slice(2);
  if (cmd !== "record") usage();

  const flags = parse_flags(rest);
  const site = flags["site"];
  const queries_json = flags["queries"];
  const out = flags["out"];
  const model_name = flags["model"] ?? DEFAULT_MODEL;

  if (!site || !queries_json || !out) usage();

  let queries: string[];
  try {
    const parsed: unknown = JSON.parse(queries_json);
    if (
      !Array.isArray(parsed) ||
      !parsed.every((q): q is string => typeof q === "string")
    ) {
      throw new Error("must be a JSON array of strings");
    }
    if (parsed.length === 0) throw new Error("must contain at least one query");
    queries = parsed;
  } catch (err) {
    console.error(`invalid --queries: ${(err as Error).message}`);
    process.exit(1);
  }

  const api_key = process.env["OPENROUTER_API_KEY"];
  if (!api_key) {
    console.error(
      "OPENROUTER_API_KEY is not set — Stagehand cannot drive the browser without it",
    );
    process.exit(1);
  }

  const out_dir = resolve(out);
  const out_path = join(out_dir, "recordings.json");

  console.error(`[recorder] site: ${site}`);
  console.error(`[recorder] model: ${model_name}`);
  console.error(`[recorder] queries: ${queries.length}`);
  console.error(`[recorder] out: ${out_dir}`);

  const persist = (recording: Recording): void => {
    mkdirSync(out_dir, { recursive: true });
    writeFileSync(out_path, JSON.stringify(recording, null, 2));
  };

  const recording = await record({
    site,
    queries,
    model_name,
    api_key,
    on_progress: persist,
  });
  persist(recording);

  const total_candidates = recording.queries.reduce(
    (s, q) => s + q.network_candidates.length,
    0,
  );
  const total_ground = recording.queries.reduce(
    (s, q) => s + q.ground_truth_products.length,
    0,
  );
  const errored = recording.queries.filter((q) => q.error).length;
  console.error(`[recorder] wrote ${out_path}`);
  console.error(
    `[recorder] ${recording.queries.length} queries (${errored} errored) · ${total_candidates} JSON responses captured · ${total_ground} ground-truth products`,
  );
}

main().catch((err: Error) => {
  console.error(`[recorder] failed: ${err.stack ?? err.message}`);
  process.exit(1);
});
