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
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | No |

## Azure Blob Storage

Production document storage should use Azure Blob Storage with a private container. The API stores only metadata and blob paths in PostgreSQL.

Recommended production rules:

- Store `AZURE_STORAGE_CONNECTION_STRING` in the deployment platform secret store.
- Keep the Blob container private.
- Do not expose public Blob URLs from the API.
- Use streamed downloads through the backend or short-lived signed URLs if direct access is later required.
- Rotate storage keys according to the organization security policy.

## GitHub Actions Image Publishing

The CI workflow publishes Docker images to GitHub Container Registry on pushes to `main`.

Image naming convention:

```text
ghcr.io/tomasz-bec-lingaro/hse:<tag>
```

Published tags:

- commit SHA
- branch name
- `latest` for the default branch

Pull requests build the image but do not push it.
