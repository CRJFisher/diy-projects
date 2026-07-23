import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { search } from "./search.js";

interface GroundTruthProduct {
  title?: string;
  url?: string;
}

interface RecordedQuery {
  query: string;
  error?: string;
  ground_truth_products?: GroundTruthProduct[];
}

interface Recording {
  site: string;
  queries: RecordedQuery[];
}

function load_recording(): Recording {
  const raw = readFileSync(
    new URL("./recordings.json", import.meta.url),
    "utf8",
  );
  return JSON.parse(raw) as Recording;
}

function is_http_url(s: string | undefined): s is string {
  return typeof s === "string" && /^https?:\/\//i.test(s);
}

function title_overlap(
  expected: GroundTruthProduct[],
  actual: Array<Record<string, unknown>>,
): number {
  if (expected.length === 0) return 1;
  const actual_titles = actual
    .map((p) => p.title)
    .filter((t): t is string => typeof t === "string")
    .map((t) => t.toLowerCase());
  const actual_urls = actual
    .map((p) => p.url)
    .filter((u): u is string => typeof u === "string");

  let hits = 0;
  for (const gt of expected) {
    const gt_title = (gt.title ?? "").toLowerCase().trim();
    let matched = false;

    if (gt_title) {
      for (const at of actual_titles) {
        if (at.includes(gt_title) || gt_title.includes(at)) {
          matched = true;
          break;
        }
      }
    }

    if (!matched && is_http_url(gt.url)) {
      const gt_url_lower = gt.url.toLowerCase();
      for (const au of actual_urls) {
        const au_lower = au.toLowerCase();
        if (
          au_lower === gt_url_lower ||
          au_lower.includes(gt_url_lower) ||
          gt_url_lower.includes(au_lower)
        ) {
          matched = true;
          break;
        }
      }
    }

    if (matched) hits++;
  }
  return hits / expected.length;
}

const recording = load_recording();
const valid_queries = recording.queries.filter((q) => !q.error);

describe("nickstimberstore.co.uk search adapter", () => {
  const overlaps: Array<{ query: string; overlap: number }> = [];

  for (const rq of valid_queries) {
    it(
      `returns products overlapping ground truth for "${rq.query}"`,
      async () => {
        const result = await search(rq.query, { max: 20 });
        expect(Array.isArray(result.products)).toBe(true);
        expect(result.products.length).toBeGreaterThan(0);
        for (const p of result.products) {
          expect(typeof p.title).toBe("string");
          expect(typeof p.url).toBe("string");
        }
        const overlap = title_overlap(
          rq.ground_truth_products ?? [],
          result.products,
        );
        overlaps.push({ query: rq.query, overlap });
      },
      120_000,
    );
  }

  it("has at most one query below 0.5 overlap", () => {
    expect(overlaps.length).toBe(valid_queries.length);
    const low_count = overlaps.filter((o) => o.overlap < 0.5).length;
    expect(low_count).toBeLessThanOrEqual(1);
  });
});
