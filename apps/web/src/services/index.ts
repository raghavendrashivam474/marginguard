/**
 * MarginGuard API services.
 *
 * Re-exports the API client and error types.
 * Future endpoint-specific service modules (e.g. organizations.ts,
 * findings.ts) will be added here as CRUD routes are implemented.
 */

export { apiClient, ApiClientError } from './client'
