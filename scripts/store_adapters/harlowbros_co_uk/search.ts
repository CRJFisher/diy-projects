import { chromium, type Browser, type Page, type Response } from "playwright-core";

const SITE_ORIGIN = "https://www.harlowbros.co.uk";
const HOME_URL = `${SITE_ORIGIN}/`;
const XSEARCH_PATH = "/amasty_xsearch/autocomplete/index/";
const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36";

// Candidate CSS selectors for the search input. Magento 2's stock theme uses
// input#search; the Amasty xsearch theme overrides this with input.amsearch-input.
// We try each in turn so the adapter survives minor theme changes.
const SEARCH_INPUT_SELECTORS: readonly string[] = [
  "input.amsearch-input",
  "input#search",
  'input[name="q"]',
];

export interface SearchOptions {
  max?: number;
}

export interface SearchResult {
  products: Array<Record<string, unknown>>;
}

interface XsearchBlock {
  type?: string;
  html?: string;
}

interface XsearchResponse {
  // Magento Amasty xsearch returns numbered keys keyed by block id (e.g. "10" for products,
  // "30" for categories) plus a "behavior" string. We only consume the product block.
  [key: string]: XsearchBlock | string | undefined;
}

function decode_html_entities(input: string): string {
  return input
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex: string) =>
      String.fromCodePoint(Number.parseInt(hex, 16)),
    )
    .replace(/&#(\d+);/g, (_, dec: string) =>
      String.fromCodePoint(Number.parseInt(dec, 10)),
    )
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&");
}

function strip_tags(input: string): string {
  return input.replace(/<[^>]+>/g, "");
}

function find_first(html: string, pattern: RegExp): string | undefined {
  const m = pattern.exec(html);
  if (!m) return undefined;
  const captured = m[1];
  return typeof captured === "string" ? captured : undefined;
}

interface ParsedProduct {
  title: string;
  url: string;
  sku?: string;
  price?: string;
  image_url?: string;
  product_id?: string;
}

function parse_product_card(card_html: string): ParsedProduct | undefined {
  // Title + url come from the canonical product-item-link <a>.
  const link_match =
    /class="amsearch-link product-item-link"\s+href="([^"]+)"\s+title="([^"]+)"/.exec(
      card_html,
    );
  if (!link_match) return undefined;
  const url_raw = link_match[1];
  const title_raw = link_match[2];
  if (typeof url_raw !== "string" || typeof title_raw !== "string") {
    return undefined;
  }

  const product: ParsedProduct = {
    title: decode_html_entities(title_raw).trim(),
    url: decode_html_entities(url_raw).trim(),
  };

  const sku_html = find_first(
    card_html,
    /<span class="amsearch-sku-block">\s*<b[^>]*>SKU:<\/b>\s*([\s\S]*?)<\/span>/,
  );
  if (sku_html !== undefined) {
    const sku = decode_html_entities(strip_tags(sku_html)).trim();
    if (sku) product.sku = sku;
  }

  const price_match = find_first(
    card_html,
    /class="price-wrapper price-including-tax"[^>]*>\s*<span class="price">([^<]+)<\/span>/,
  );
  if (price_match !== undefined) {
    product.price = decode_html_entities(price_match).trim();
  } else {
    const fallback_price = find_first(
      card_html,
      /<span class="price">([^<]+)<\/span>/,
    );
    if (fallback_price !== undefined) {
      product.price = decode_html_entities(fallback_price).trim();
    }
  }

  const image_match = find_first(
    card_html,
    /<img[^>]+class="product-image-photo"[^>]+src="([^"]+)"/,
  );
  if (image_match !== undefined) {
    product.image_url = decode_html_entities(image_match).trim();
  }

  const id_match = find_first(card_html, /data-product-id="(\d+)"/);
  if (id_match !== undefined) {
    product.product_id = id_match;
  }

  return product;
}

function parse_xsearch_html(block_html: string): ParsedProduct[] {
  const cards = block_html.split(
    /(?=<li class="amsearch-item product-item")/,
  );
  const products: ParsedProduct[] = [];
  for (const card of cards) {
    if (!card.includes('class="amsearch-item product-item"')) continue;
    const parsed = parse_product_card(card);
    if (parsed) products.push(parsed);
  }
  return products;
}

function product_block(response: XsearchResponse): XsearchBlock | undefined {
  for (const value of Object.values(response)) {
    if (
      value &&
      typeof value === "object" &&
      "type" in value &&
      value.type === "product" &&
      typeof value.html === "string"
    ) {
      return value;
    }
  }
  return undefined;
}

async function find_search_input(page: Page): Promise<string> {
  for (const selector of SEARCH_INPUT_SELECTORS) {
    const handle = await page.$(selector);
    if (handle) {
      await handle.dispose();
      return selector;
    }
  }
  throw new Error(
    `search: could not locate search input on ${HOME_URL} (tried ${SEARCH_INPUT_SELECTORS.join(", ")})`,
  );
}

async function fetch_xsearch_via_typing(
  browser: Browser,
  query: string,
): Promise<XsearchResponse> {
  const context = await browser.newContext({ userAgent: USER_AGENT });
  try {
    const page = await context.newPage();
    // The xsearch endpoint is gated by Magento session cookies + a per-session form_key
    // and rejects synthesized fetch() calls (HTTP 403). The request only succeeds when
    // it is fired the way the page itself fires it: by typing into the search input,
    // which lets the Amasty xsearch JS attach the correct uenc + form_key + cookies.
    // We replay that interaction and capture the response with waitForResponse.
    await page.goto(HOME_URL, {
      waitUntil: "domcontentloaded",
      timeout: 45_000,
    });

    const input_selector = await find_search_input(page);
    await page.click(input_selector);

    const response_promise: Promise<Response> = page.waitForResponse(
      (resp) => {
        const url = resp.url();
        if (!url.startsWith(SITE_ORIGIN)) return false;
        if (!url.includes(XSEARCH_PATH)) return false;
        return resp.status() === 200;
      },
      { timeout: 30_000 },
    );

    // Magento's xsearch debounces typed input. fill() inserts the whole string at once,
    // which the bundled JS treats as a single edit and dispatches the autocomplete XHR.
    await page.fill(input_selector, query);

    const response = await response_promise;
    const text = await response.text();
    const parsed: unknown = JSON.parse(text);
    if (!parsed || typeof parsed !== "object") {
      throw new Error("xsearch: response was not a JSON object");
    }
    return parsed as XsearchResponse;
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
  const max = opts.max ?? Number.POSITIVE_INFINITY;

  await new Promise((resolve) => setTimeout(resolve, 250));

  const browser = await chromium.launch({ headless: true });
  try {
    const response = await fetch_xsearch_via_typing(browser, query);
    const block = product_block(response);
    if (!block || typeof block.html !== "string") {
      // No product block means the query returned zero suggestions; emit empty list.
      return { products: [] };
    }
    const parsed_products = parse_xsearch_html(block.html);
    const products: Array<Record<string, unknown>> = parsed_products.map(
      (p) => {
        const out: Record<string, unknown> = {
          title: p.title,
          url: p.url,
        };
        if (p.sku !== undefined) out.sku = p.sku;
        if (p.price !== undefined) out.price = p.price;
        if (p.image_url !== undefined) out.image_url = p.image_url;
        if (p.product_id !== undefined) out.product_id = p.product_id;
        return out;
      },
    );
    return { products: products.slice(0, max) };
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
