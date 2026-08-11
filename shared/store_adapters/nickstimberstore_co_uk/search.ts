import { chromium, type Browser } from "playwright-core";

const SEARCH_URL_TEMPLATE =
  "https://www.nickstimberstore.co.uk/search?q={query}";
const PRODUCT_LINK_SELECTOR = 'a[href*="/products/"]';
const ORIGIN = "https://www.nickstimberstore.co.uk";
const NAVIGATION_TIMEOUT_MS = 45_000;
const SELECTOR_TIMEOUT_MS = 30_000;

export interface SearchOptions {
  max?: number;
}

export interface SearchResult {
  products: Array<Record<string, unknown>>;
}

interface ScrapedProduct {
  title: string;
  url: string;
  image_url: string;
  price: string;
}

async function scrape_results(
  browser: Browser,
  query: string,
): Promise<ScrapedProduct[]> {
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    locale: "en-GB",
    viewport: { width: 1280, height: 1800 },
  });
  try {
    const page = await context.newPage();
    page.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT_MS);
    page.setDefaultTimeout(SELECTOR_TIMEOUT_MS);

    // tsx injects `__name(fn, "label")` annotations into transpiled callbacks;
    // those references survive into the function body Playwright serializes
    // for $$eval, but `__name` is not defined in the page context. Stub it.
    await page.addInitScript(() => {
      const g = globalThis as typeof globalThis & {
        __name?: <T>(fn: T, label?: string) => T;
      };
      if (g.__name === undefined) {
        g.__name = (fn) => fn;
      }
    });

    const url = SEARCH_URL_TEMPLATE.replace(
      "{query}",
      encodeURIComponent(query),
    );

    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page
      .waitForSelector(PRODUCT_LINK_SELECTOR, { timeout: SELECTOR_TIMEOUT_MS })
      .catch(() => {
        // No product links — return empty rather than throw, to allow the
        // caller to distinguish "site loaded but no results" from network failure.
      });

    const raw = await page.$$eval(PRODUCT_LINK_SELECTOR, (anchors) => {
      const text_of = (el: Element | null | undefined): string => {
        if (!el) return "";
        const t = el.textContent;
        return typeof t === "string" ? t.replace(/\s+/g, " ").trim() : "";
      };

      const find_card = (a: HTMLAnchorElement): Element => {
        let cur: Element | null = a;
        while (cur && cur.parentElement) {
          const parent: HTMLElement = cur.parentElement;
          const tag = parent.tagName.toLowerCase();
          if (tag === "li" || tag === "article") return parent;
          const cls = parent.className;
          if (
            typeof cls === "string" &&
            /(product-card|product-item|grid__item|card-wrapper|product-grid-item)/i.test(
              cls,
            )
          ) {
            return parent;
          }
          cur = parent;
          if (parent === document.body) break;
        }
        return a;
      };

      const seen = new Set<string>();
      const out: Array<{
        title: string;
        url: string;
        image_url: string;
        price: string;
      }> = [];

      for (const node of anchors) {
        const a = node as HTMLAnchorElement;
        const href_raw = a.getAttribute("href");
        if (!href_raw) continue;
        // Skip non-product links: pagination, filters, variants embedded in
        // links to /products/ are still valid; we only filter empty/javascript.
        if (href_raw.startsWith("#") || href_raw.toLowerCase().startsWith("javascript:")) {
          continue;
        }

        // Resolve to absolute URL using the document's base.
        let href = href_raw;
        try {
          href = new URL(href_raw, document.baseURI).toString();
        } catch {
          continue;
        }
        // Drop query params/fragments to dedupe variant links.
        let dedupe_key = href;
        try {
          const u = new URL(href);
          dedupe_key = `${u.origin}${u.pathname}`;
        } catch {
          /* keep as-is */
        }
        if (seen.has(dedupe_key)) continue;

        const card = find_card(a);

        // Title: prefer non-empty anchor text; fall back to a heading inside the card.
        let title = text_of(a);
        if (!title) {
          const heading =
            card.querySelector("h1, h2, h3, h4, .product-title, .card__heading, .product-card__title");
          title = text_of(heading);
        }
        // If anchor only contains an image, look for an aria-label or title attr.
        if (!title) {
          const aria = a.getAttribute("aria-label");
          if (typeof aria === "string") title = aria.trim();
        }
        if (!title) {
          const tt = a.getAttribute("title");
          if (typeof tt === "string") title = tt.trim();
        }
        if (!title) continue;

        // Image
        let image_url = "";
        const img = card.querySelector("img");
        if (img) {
          const src =
            img.getAttribute("src") ||
            img.getAttribute("data-src") ||
            img.getAttribute("data-srcset") ||
            "";
          if (src) {
            const first = src.split(",")[0];
            if (first) image_url = first.trim().split(" ")[0] ?? "";
            try {
              image_url = new URL(image_url, document.baseURI).toString();
            } catch {
              /* leave as-is */
            }
          }
        }

        // Price: scan card text for a £ value.
        let price = "";
        const card_text = text_of(card);
        const m = card_text.match(/£\s?\d[\d,]*(?:\.\d{1,2})?(?:\s*\+\s*VAT)?/i);
        if (m) price = m[0].replace(/\s+/g, " ").trim();

        seen.add(dedupe_key);
        out.push({ title, url: href, image_url, price });
      }
      return out;
    });

    return raw;
  } finally {
    await context.close();
  }
}

export async function search(
  query: string,
  opts: SearchOptions = {},
): Promise<SearchResult> {
  if (!query || !query.trim()) {
    throw new Error("search: query must be a non-empty string");
  }
  const max = opts.max ?? Infinity;

  await new Promise((r) => setTimeout(r, 250));

  const browser = await chromium.launch({ headless: true });
  try {
    const scraped = await scrape_results(browser, query);

    const products: Array<Record<string, unknown>> = scraped.map((p) => {
      const out: Record<string, unknown> = {
        title: p.title,
        url: p.url,
      };
      if (p.image_url) out.image_url = p.image_url;
      if (p.price) out.price = p.price;
      return out;
    });

    return { products: products.slice(0, max) };
  } finally {
    await browser.close();
  }
}

function parse_args(argv: string[]): {
  query: string;
  max: number | undefined;
} {
  let query = "";
  let max: number | undefined;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--max") {
      const next = argv[i + 1];
      if (next === undefined) throw new Error("--max requires a value");
      const n = Number.parseInt(next, 10);
      if (!Number.isFinite(n) || n <= 0) {
        throw new Error(`--max must be a positive integer, got ${next}`);
      }
      max = n;
      i++;
    } else if (!query && typeof a === "string") {
      query = a;
    }
  }
  if (!query) throw new Error("usage: tsx search.ts <query> [--max N]");
  return { query, max };
}

const is_main = (() => {
  const entry = process.argv[1];
  if (!entry) return false;
  try {
    const url = new URL(import.meta.url);
    return url.pathname.endsWith(entry) || entry.endsWith("search.ts");
  } catch {
    return false;
  }
})();

// Reference ORIGIN to silence unused-var checks if tree-shaken; it documents
// the host this adapter targets.
void ORIGIN;

if (is_main) {
  const { query, max } = parse_args(process.argv.slice(2));
  search(query, max === undefined ? {} : { max })
    .then((result) => {
      process.stdout.write(JSON.stringify(result));
    })
    .catch((err: unknown) => {
      const msg = err instanceof Error ? err.message : String(err);
      process.stderr.write(`${msg}\n`);
      process.exit(1);
    });
}
