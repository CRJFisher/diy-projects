import { chromium } from "playwright-core";

const SITE_ORIGIN = "https://www.thetimbergroup.co.uk";
const AUTOCOMPLETE_URL_TEMPLATE = `${SITE_ORIGIN}/search/autocomplete/{query}`;
const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36";

const CARD_SELECTOR = "a.searchFormAC";
const NO_RESULTS_SELECTOR = "a.searchFormAC, p.searchFormAC, .searchFormAC";

export interface SearchOptions {
  max?: number;
}

export interface SearchResult {
  products: Array<Record<string, unknown>>;
}

interface ScrapedProduct {
  title: string;
  url: string;
  price?: string;
}

function build_autocomplete_url(query: string): string {
  return AUTOCOMPLETE_URL_TEMPLATE.replace(
    "{query}",
    encodeURIComponent(query),
  );
}

function resolve_url(href: string): string {
  if (/^https?:\/\//i.test(href)) return href;
  if (href.startsWith("/")) return `${SITE_ORIGIN}${href}`;
  return `${SITE_ORIGIN}/${href}`;
}

export async function search(
  query: string,
  opts: SearchOptions = {},
): Promise<SearchResult> {
  if (!query || !query.trim()) {
    throw new Error("search: query must be a non-empty string");
  }
  const max = opts.max ?? Number.POSITIVE_INFINITY;

  await new Promise((resolve) => setTimeout(resolve, 250));

  const url = build_autocomplete_url(query);

  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ userAgent: USER_AGENT });
    try {
      const page = await context.newPage();
      await page.goto(url, {
        waitUntil: "domcontentloaded",
        timeout: 45_000,
      });

      // Wait for either a real product card or the no-results / branch-selector
      // card; the autocomplete page always renders at least one searchFormAC element.
      await page.waitForSelector(NO_RESULTS_SELECTOR, { timeout: 30_000 });

      const scraped: ScrapedProduct[] = await page.$$eval(
        CARD_SELECTOR,
        (anchors) => {
          const out: ScrapedProduct[] = [];
          for (const a of anchors) {
            const el = a as HTMLAnchorElement;

            // Skip the branch-selector card and any non-product variant.
            if (el.classList.contains("storeSel")) continue;

            const description_el = el.querySelector("p#description");
            const title_text = description_el
              ? (description_el.textContent ?? "").trim()
              : "";
            if (!title_text) continue;

            // Skip the "no results" card. Its <p id="description"> says
            // "There are no results for this search, please try again.".
            if (/no results for this search/i.test(title_text)) continue;

            const href = el.getAttribute("href") ?? "";
            if (!href) continue;

            const product: ScrapedProduct = {
              title: title_text,
              url: href,
            };

            // The card has two <span class="price"> elements: ex-VAT inside a
            // <p style="display: none"> and inc-VAT inside a visible <p>. The
            // hidden flag lives on the parent <p>, not the span itself, so walk
            // up and skip any span whose ancestor (within this card) is hidden.
            const price_spans = el.querySelectorAll("span.price");
            let price_text = "";
            for (const span of price_spans) {
              let hidden = false;
              let node: HTMLElement | null = span as HTMLElement;
              while (node && node !== el) {
                if (node.style && node.style.display === "none") {
                  hidden = true;
                  break;
                }
                node = node.parentElement;
              }
              if (hidden) continue;
              const txt = (span.textContent ?? "").trim();
              if (txt) {
                price_text = txt;
                break;
              }
            }
            if (price_text) product.price = price_text;

            out.push(product);
          }
          return out;
        },
      );

      const products: Array<Record<string, unknown>> = scraped.map((p) => {
        const out: Record<string, unknown> = {
          title: p.title,
          url: resolve_url(p.url),
        };
        if (p.price !== undefined) out.price = p.price;
        return out;
      });

      return { products: products.slice(0, max) };
    } finally {
      await context.close();
    }
  } finally {
    await browser.close();
  }
}

interface CliArgs {
  query: string;
  max?: number;
}

function parse_args(argv: string[]): CliArgs {
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
  return max === undefined ? { query } : { query, max };
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

if (is_main) {
  const args = parse_args(process.argv.slice(2));
  const opts: SearchOptions = args.max === undefined ? {} : { max: args.max };
  search(args.query, opts)
    .then((result) => {
      process.stdout.write(JSON.stringify(result));
    })
    .catch((err: unknown) => {
      const msg = err instanceof Error ? err.message : String(err);
      process.stderr.write(`${msg}\n`);
      process.exit(1);
    });
}
