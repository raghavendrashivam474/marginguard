/**
 * MarginGuard API client.
 *
 * Centralized HTTP client for all backend communication.
 * Do NOT place direct fetch() calls in React components.
 *
 * Usage:
 *   import { apiClient } from "@/services";
 *   const data = await apiClient.get<Organization>("/api/v1/organizations/123");
 */

import type { ApiErrorResponse } from "@/types";

const DEFAULT_BASE_URL = "http://localhost:8000";

export class ApiClientError extends Error {
  constructor(
    public status: number,
    public body: ApiErrorResponse,
  ) {
    super(body.error.message);
    this.name = "ApiClientError";
  }
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl =
      baseUrl ??
      import.meta.env.VITE_API_BASE_URL ??
      DEFAULT_BASE_URL;
  }

  private async request<T>(
    method: string,
    path: string,
    options?: {
      body?: unknown;
      params?: Record<string, string | number | undefined>;
    },
  ): Promise<T> {
    const url = new URL(path, this.baseUrl);

    if (options?.params) {
      for (const [key, value] of Object.entries(options.params)) {
        if (value !== undefined) {
          url.searchParams.set(key, String(value));
        }
      }
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: options?.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      let errorBody: ApiErrorResponse;
      try {
        errorBody = (await response.json()) as ApiErrorResponse;
      } catch {
        errorBody = {
          error: {
            code: "UNKNOWN_ERROR",
            message: `HTTP ${response.status}: ${response.statusText}`,
            details: [],
            request_id: null,
          },
        };
      }
      throw new ApiClientError(response.status, errorBody);
    }

    return (await response.json()) as T;
  }

  async get<T>(
    path: string,
    params?: Record<string, string | number | undefined>,
  ): Promise<T> {
    return this.request<T>("GET", path, { params });
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("POST", path, { body });
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PUT", path, { body });
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PATCH", path, { body });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
}

/** Singleton API client instance. */
export const apiClient = new ApiClient();
