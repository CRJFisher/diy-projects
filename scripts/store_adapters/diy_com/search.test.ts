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

function loadRecording(): Recording {
  const raw = readFileSync(
    new URL("./recordings.json", import.meta.url),
    "utf8",
  );
  return JSON.parse(raw) as Recording;
}

function isHttpUrl(s: string | undefined): s is string {
  return typeof s === "string" && /^https?:\/\//i.test(s);
}

function titleOverlap(
  expected: GroundTruthProduct[],
  actual: Array<Record<string, unknown>>,
): number {
  if (expected.length === 0) return 1;
  const actualTitles = actual
    .map((p) => p.title)
    .filter((t): t is string => typeof t === "string")
    .map((t) => t.toLowerCase());
  const actualUrls = actual
    .map((p) => p.url)
    .filter((u): u is string => typeof u === "string");

  let hits = 0;
  for (const gt of expected) {
    const gtTitle = (gt.title ?? "").toLowerCase().trim();
    let matched = false;

    if (gtTitle) {
      for (const at of actualTitles) {
        if (at.includes(gtTitle) || gtTitle.includes(at)) {
          matched = true;
          break;
        }
      }
    }

    if (!matched && isHttpUrl(gt.url)) {
      const gtUrlLower = gt.url.toLowerCase();
      for (const au of actualUrls) {
        const auLower = au.toLowerCase();
        if (auLower === gtUrlLower || auLower.includes(gtUrlLower) || gtUrlLower.includes(auLower)) {
          matched = true;
          break;
        }
      }
    }

    if (matched) hits++;
  }
  return hits / expected.length;
}

const recording = loadRecording();
const validQueries = recording.queries.filter((q) => !q.error);

describe("diy.com search adapter", () => {
  const overlaps: Array<{ query: string; overlap: number }> = [];

  for (const rq of validQueries) {
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
        const overlap = titleOverlap(
          rq.ground_truth_products ?? [],
          result.products,
        );
        overlaps.push({ query: rq.query, overlap });
      },
      60_000,
    );
  }

  it("has at most one query below 0.5 overlap", () => {
    expect(overlaps.length).toBe(validQueries.length);
    const lowCount = overlaps.filter((o) => o.overlap < 0.5).length;
    expect(lowCount).toBeLessThanOrEqual(1);
  });
});
