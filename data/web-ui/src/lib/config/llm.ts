/**
 * LLM Processor API Configuration
 */
export const LLM_API_BASE_URL =
  import.meta.env.VITE_LLM_API_BASE_URL || 'http://llm-processor-mailcow:8080';

/**
 * Build a full URL for an LLM API endpoint
 */
export function buildLlmApiUrl(path: string, params?: Record<string, string | number | boolean>): string {
  // Ensure path starts with a leading slash
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(normalizedPath, LLM_API_BASE_URL);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, String(value));
    });
  }
  return url.toString();
}
