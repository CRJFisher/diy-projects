import { z } from "zod";

const SEARCH_URL_TEMPLATE = "https://www.diy.com/search?term={query}";
const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36";

const OfferSchema = z
  .object({
    "@type": z.string().optional(),
    priceCurrency: z.string().optional(),
    price: z.union([z.number(), z.string()]).optional(),
  })
  .partial();

const ItemSchema = z
  .object({
    "@type": z.string().optional(),
    position: z.number().optional(),
    image: z.string().optional(),
    url: z.string(),
    name: z.string(),
    sku: z.string().optional(),
    description: z.string().optional(),
    offers: OfferSchema.optional(),
  })
  .passthrough();

const ItemListSchema = z
  .object({
    "@type": z.string(),
    numberOfItems: z.number().optional(),
    itemListElement: z.array(ItemSchema),
  })
  .passthrough();

export interface SearchOptions {
  max?: number;
}

export interface SearchResult {
  products: Array<Record<string, unknown>>;
}

function decodeHtmlEntities(input: string): string {
  return input
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&");
}

function extractLdJsonScripts(html: string): string[] {
  const re =
    /<script\b[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  const out: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) {
    const body = m[1];
    if (typeof body === "string") out.push(body);
  }
  return out;
}

function findItemList(html: string): z.infer<typeof ItemListSchema> | null {
  for (const raw of extractLdJsonScripts(html)) {
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch {
      continue;
    }
    const candidates: unknown[] = Array.isArray(parsed) ? parsed : [parsed];
    for (const c of candidates) {
      if (
        c &&
        typeof c === "object" &&
        (c as { "@type"?: unknown })["@type"] === "ItemList"
      ) {
        const result = ItemListSchema.safeParse(c);
        if (result.success) return result.data;
      }
    }
  }
  return null;
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

  const url = SEARCH_URL_TEMPLATE.replace(
    "{query}",
    encodeURIComponent(query),
  );

  const res = await fetch(url, {
    method: "GET",
    headers: {
      accept: "text/html,application/xhtml+xml",
      "user-agent": USER_AGENT,
    },
  });

  if (!res.ok) {
    throw new Error(
      `search: diy.com returned HTTP ${res.status} for ${url}`,
    );
  }

  const html = await res.text();
  const list = findItemList(html);
  if (!list) {
    throw new Error(
      "search: could not locate <script type=\"application/ld+json\"> ItemList in diy.com search page",
    );
  }

  const products: Array<Record<string, unknown>> = list.itemListElement.map(
    (item) => {
      const out: Record<string, unknown> = {
        title: decodeHtmlEntities(item.name),
        url: item.url,
      };
      if (typeof item.sku === "string") out.sku = item.sku;
      if (typeof item.image === "string")
        out.image_url = decodeHtmlEntities(item.image);
      if (typeof item.description === "string")
        out.description = decodeHtmlEntities(item.description);
      if (typeof item.position === "number") out.position = item.position;
      const offers = item.offers;
      if (offers) {
        if (typeof offers.price === "number" || typeof offers.price === "string") {
          out.price = offers.price;
        }
        if (typeof offers.priceCurrency === "string") {
          out.price_currency = offers.priceCurrency;
        }
      }
      return out;
    },
  );

  return { products: products.slice(0, max) };
}

function parseArgs(argv: string[]): { query: string; max: number | undefined } {
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
    } else if (!query) {
      query = a ?? "";
    }
  }
  if (!query) throw new Error("usage: tsx search.ts <query> [--max N]");
  return { query, max };
}

const isMain = (() => {
  const entry = process.argv[1];
  if (!entry) return false;
  try {
    const url = new URL(import.meta.url);
    return url.pathname.endsWith(entry) || entry.endsWith("search.ts");
  } catch {
    return false;
  }
})();

if (isMain) {
  const { query, max } = parseArgs(process.argv.slice(2));
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
