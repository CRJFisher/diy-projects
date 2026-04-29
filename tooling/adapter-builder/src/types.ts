import { z } from "zod";

export const GroundTruthProductSchema = z.object({
  title: z.string(),
  price: z.string().optional(),
  url: z.string().optional(),
  in_stock: z.union([z.boolean(), z.string()]).optional(),
  image_url: z.string().optional(),
});

export type GroundTruthProduct = z.infer<typeof GroundTruthProductSchema>;

export const ExtractionSchema = z.object({
  products: z.array(GroundTruthProductSchema),
});

export type NetworkCandidate = {
  url: string;
  method: string;
  resource_type: string;
  status: number;
  request_headers: Record<string, string>;
  post_data: string | null;
  response_headers: Record<string, string>;
  content_type: string;
  body: unknown;
  body_truncated: boolean;
  body_text_sample?: string;
};

export type FailedRequest = {
  url: string;
  method: string;
  resource_type: string;
  failure: string;
};

export type QueryRecording = {
  query: string;
  final_url: string;
  network_candidates: NetworkCandidate[];
  failed_requests: FailedRequest[];
  ground_truth_products: GroundTruthProduct[];
  error?: string;
};

export type Recording = {
  site: string;
  captured_at: string;
  queries: QueryRecording[];
};
