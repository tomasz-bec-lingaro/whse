# Production Configuration

This service is configured through environment variables. Real secrets must be injected by the runtime platform or CI/CD secret storage. They must not be committed to the repository.

## Required Runtime Variables

| Variable | Purpose | Secret |
| --- | --- | --- |
| `APP_ENV` | Runtime environment name, for example `production` | No |
| `LOG_LEVEL` | Application log level | No |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Blob Storage connection string | Yes |
| `AZURE_STORAGE_CONTAINER_NAME` | Blob container for delivery documents | No |
| `MAX_UPLOAD_SIZE_MB` | Maximum accepted upload size | No |
| `UPLOAD_RATE_LIMIT_PER_MINUTE` | Maximum document upload requests per client in the configured window | No |
| `UPLOAD_RATE_LIMIT_WINDOW_SECONDS` | Upload rate-limit window duration in seconds | No |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | No |
| `API_KEY` | API key required by non-health endpoints | Yes |
| `API_KEY_ROLES` | Comma-separated roles granted to the API key | No |

## API Access Control

All endpoints except `/health` require the `X-API-Key` header. For this MVP the application enforces the `whs:operator` role through `API_KEY_ROLES`.

Production rules:

- Store `API_KEY` in the deployment platform secret store.
- Rotate `API_KEY` according to the organization security policy.
- Expose the API only through the intended authenticated ingress, API gateway, or private network boundary.
- If a corporate identity provider is available, replace the static API key with gateway-verified identity or OIDC/JWT validation.

## Azure Blob Storage

Production document storage should use Azure Blob Storage with a private container. The API stores only metadata and blob paths in PostgreSQL.

Recommended production rules:

- Store `AZURE_STORAGE_CONNECTION_STRING` in the deployment platform secret store.
- Keep the Blob container private.
- Disable account-level public Blob access.
- Do not expose public Blob URLs from the API.
- Use streamed downloads through the backend or short-lived signed URLs if direct access is later required.
- Soft delete should not delete the blob object; use a separate lifecycle process if physical cleanup is required later.
- Rotate storage keys according to the organization security policy.

## Rate Limiting

Document upload endpoints use an in-memory per-client rate limiter for the MVP. This protects a
single service instance against accidental or abusive bursts. For multi-replica production
deployments, enforce the same limits in the API gateway or replace the in-memory limiter with a
shared backend such as Redis.

## Production Validation Checklist

- Confirm the production ingress or gateway requires the expected identity before forwarding traffic.
- Confirm direct public access to the API container is blocked unless the API itself is the intended public boundary.
- Confirm the Azure Blob container is private and public access is disabled.
- Confirm `DATABASE_URL`, `AZURE_STORAGE_CONNECTION_STRING`, and `API_KEY` are injected from secrets.
- Confirm application logs do not contain document bytes, storage connection strings, or API keys.

## GitHub Actions Image Publishing

The CI workflow builds on pull requests, pushes to `main`, and manual dispatch. It publishes Docker images to GitHub Container Registry only on pushes to `main`.

Image naming convention:

```text
ghcr.io/tomasz-bec-lingaro/hse:<tag>
```

Published tags:

- commit SHA
- branch name
- `latest` for the default branch

Pull requests build the image but do not push it.

Manual `workflow_dispatch` runs execute validation and Docker build only. They do not publish images.
