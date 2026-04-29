import { Stagehand } from "@browserbasehq/stagehand";
import {
  chromium,
  type BrowserContext,
  type Page,
  type Request,
  type Response,
} from "playwright-core";
import {
  ExtractionSchema,
  type FailedRequest,
  type NetworkCandidate,
  type QueryRecording,
  type Recording,
} from "./types.js";

const MAX_BODY_BYTES = 4 * 1024 * 1024;
const BODY_TEXT_SAMPLE_BYTES = 16 * 1024;
const NETWORKIDLE_TIMEOUT_MS = 15_000;
const PAGE_LOAD_TIMEOUT_MS = 30_000;
const QUERY_DEADLINE_MS = 120_000;
const STAGEHAND_RETRY_ATTEMPTS = 3;
const STAGEHAND_CLOSE_TIMEOUT_MS = 10_000;
const OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1";

const STEALTH_LAUNCH_ARGS = ["--disable-blink-features=AutomationControlled"];

export type RecordOptions = {
  site: string;
  queries: string[];
  model_name: string;
  api_key: string;
  on_progress: (recording: Recording) => void;
};

export async function record(opts: RecordOptions): Promise<Recording> {
  const { site, queries, model_name, api_key, on_progress } = opts;

  const stagehand = new Stagehand({
    env: "LOCAL",
    model: {
      modelName: model_name,
      provider: "openai",
      baseURL: OPENROUTER_BASE_URL,
      apiKey: api_key,
    },
    localBrowserLaunchOptions: {
      args: STEALTH_LAUNCH_ARGS,
    },
  });

  const recording: Recording = {
    site,
    captured_at: new Date().toISOString(),
    queries: [],
  };

  try {
    await stagehand.init();
    const browser = await chromium.connectOverCDP(stagehand.connectURL());
    const context = browser.contexts()[0];
    if (!context) throw new Error("CDP browser exposed no context");
    const page = context.pages()[0] ?? (await context.newPage());

    for (const query of queries) {
      console.error(`[recorder] running query: ${query}`);
      const query_recording = await run_query_with_deadline({
        stagehand,
        context,
        page,
        site,
        query,
      });
      recording.queries.push(query_recording);
      on_progress(recording);
      console.error(
        query_recording.error
          ? `[recorder]   error: ${query_recording.error}`
          : `[recorder]   captured ${query_recording.network_candidates.length} JSON responses, ${query_recording.failed_requests.length} failed requests, ${query_recording.ground_truth_products.length} visible products`,
      );
    }
  } finally {
    await close_with_timeout(stagehand);
  }

  return recording;
}

async function close_with_timeout(stagehand: Stagehand): Promise<void> {
  const timeout = new Promise<"timeout">((resolve) => {
    setTimeout(() => resolve("timeout"), STAGEHAND_CLOSE_TIMEOUT_MS);
  });
  const close = stagehand
    .close()
    .then(() => "closed" as const)
    .catch((err: Error) => {
      console.error(`[recorder] stagehand.close() threw: ${err.message}`);
      return "errored" as const;
    });
  const result = await Promise.race([close, timeout]);
  if (result === "timeout") {
    console.error(
      `[recorder] stagehand.close() did not return within ${STAGEHAND_CLOSE_TIMEOUT_MS}ms — leaking`,
    );
  }
}

async function run_query_with_deadline(args: {
  stagehand: Stagehand;
  context: BrowserContext;
  page: Page;
  site: string;
  query: string;
}): Promise<QueryRecording> {
  const deadline = new Promise<QueryRecording>((_, reject) => {
    setTimeout(
      () => reject(new Error(`query exceeded ${QUERY_DEADLINE_MS}ms deadline`)),
      QUERY_DEADLINE_MS,
    );
  });
  try {
    return await Promise.race([run_query(args), deadline]);
  } catch (err) {
    return {
      query: args.query,
      final_url: args.page.url(),
      network_candidates: [],
      failed_requests: [],
      ground_truth_products: [],
      error: (err as Error).message,
    };
  }
}

async function run_query(args: {
  stagehand: Stagehand;
  context: BrowserContext;
  page: Page;
  site: string;
  query: string;
}): Promise<QueryRecording> {
  const { stagehand, context, page, site, query } = args;

  const candidates: NetworkCandidate[] = [];
  const failed_requests: FailedRequest[] = [];
  const in_flight: Promise<void>[] = [];

  const on_response = (response: Response): void => {
    in_flight.push(capture_response(response, candidates));
  };
  const on_failed = (request: Request): void => {
    failed_requests.push({
      url: request.url(),
      method: request.method(),
      resource_type: request.resourceType(),
      failure: request.failure()?.errorText ?? "unknown",
    });
  };
  const on_new_page = (new_page: Page): void => {
    new_page.on("response", on_response);
    new_page.on("requestfailed", on_failed);
  };

  context.on("page", on_new_page);
  for (const existing_page of context.pages()) {
    existing_page.on("response", on_response);
    existing_page.on("requestfailed", on_failed);
  }

  try {
    await page.goto(site, {
      waitUntil: "domcontentloaded",
      timeout: PAGE_LOAD_TIMEOUT_MS,
    });

    await retry_stagehand(() =>
      stagehand.act(
        "If a cookie consent banner, GDPR notice, or 'accept all cookies' dialog is visible, click the accept-all or dismiss button. If no banner is visible, do nothing.",
      ),
    );

    await retry_stagehand(() =>
      stagehand.act(
        "Locate the main product search input on this page and click on it to focus it.",
      ),
    );

    await retry_stagehand(() =>
      stagehand.act(
        `Type "${query}" into the focused search input, then submit the search by pressing Enter or clicking the submit button.`,
      ),
    );

    await page
      .waitForLoadState("networkidle", { timeout: NETWORKIDLE_TIMEOUT_MS })
      .catch(() => {});

    const extract_result = await retry_stagehand(() =>
      stagehand.extract(
        "Extract every visible product card on this search results page. For each card, capture: title (the product name), price (the visible price text including currency, if shown), url (the link to the product page), in_stock (any stock or availability indicator visible on the card), image_url (the product image src). Skip any 'sponsored' or advert blocks if they are clearly distinct from organic results.",
        ExtractionSchema,
      ),
    );

    const products = extract_result.products ?? [];

    if (products.length === 0) {
      const html_snippet = (await page.content().catch(() => "")).slice(0, 400);
      throw new Error(
        `search for "${query}" produced no visible product cards on ${page.url()}. Page snippet: ${html_snippet.replace(/\s+/g, " ")}`,
      );
    }

    await Promise.allSettled(in_flight);

    return {
      query,
      final_url: page.url(),
      network_candidates: candidates,
      failed_requests,
      ground_truth_products: products,
    };
  } finally {
    context.off("page", on_new_page);
    for (const p of context.pages()) {
      p.off("response", on_response);
      p.off("requestfailed", on_failed);
    }
  }
}

async function capture_response(
  response: Response,
  candidates: NetworkCandidate[],
): Promise<void> {
  const request = response.request();
  const resource_type = request.resourceType();
  if (resource_type !== "xhr" && resource_type !== "fetch") return;

  const status = response.status();
  if (status < 200 || status >= 400) return;

  const response_headers = response.headers();
  const content_type = response_headers["content-type"] ?? "";
  if (!/json|javascript|graphql/i.test(content_type)) return;

  let body_text: string;
  try {
    body_text = await response.text();
  } catch (err) {
    console.error(
      `[recorder] could not read body for ${response.url()}: ${(err as Error).name}`,
    );
    return;
  }

  let body: unknown = null;
  let body_truncated = false;
  let body_text_sample: string | undefined;

  if (body_text.length > MAX_BODY_BYTES) {
    body_truncated = true;
    body_text_sample = body_text.slice(0, BODY_TEXT_SAMPLE_BYTES);
  } else {
    try {
      body = JSON.parse(body_text);
    } catch {
      return;
    }
  }

  const candidate: NetworkCandidate = {
    url: response.url(),
    method: request.method(),
    resource_type,
    status,
    request_headers: request.headers(),
    post_data: request.postData(),
    response_headers,
    content_type,
    body,
    body_truncated,
  };
  if (body_text_sample !== undefined) {
    candidate.body_text_sample = body_text_sample;
  }
  candidates.push(candidate);
}

async function retry_stagehand<T>(fn: () => Promise<T>): Promise<T> {
  let last_err: Error | undefined;
  for (let attempt = 1; attempt <= STAGEHAND_RETRY_ATTEMPTS; attempt++) {
    try {
      return await fn();
    } catch (err) {
      last_err = err as Error;
      const transient = /429|timeout|temporar|503|502|504|fetch failed/i.test(
        last_err.message ?? "",
      );
      if (!transient || attempt === STAGEHAND_RETRY_ATTEMPTS) throw last_err;
      const delay_ms = 1000 * Math.pow(4, attempt - 1);
      console.error(
        `[recorder] stagehand call failed (attempt ${attempt}/${STAGEHAND_RETRY_ATTEMPTS}): ${last_err.message} — retrying in ${delay_ms}ms`,
      );
      await new Promise((r) => setTimeout(r, delay_ms));
    }
  }
  throw last_err ?? new Error("retry_stagehand: unreachable");
}
