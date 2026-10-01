# GitHub Repository Setup

Repository:

```text
git@github.com:tomasz-bec-lingaro/whse.git
```

## Local Git Initialization

The local repository should be initialized with:

```bash
git init
git remote add origin git@github.com:tomasz-bec-lingaro/whse.git
git branch -M main
```

Do not run `git push` until the repository is reviewed and ready.

## GitHub Actions Build

The workflow in `.github/workflows/ci.yml` runs on:

- pull requests
- pushes to `main`
- manual `workflow_dispatch`

The workflow:

- installs Poetry dependencies from `poetry.lock`
- runs Ruff linting
- checks formatting
- runs pytest with coverage
- builds the Docker image
- publishes the image to GitHub Container Registry only on pushes to `main`

Image path:

```text
ghcr.io/tomasz-bec-lingaro/whse:<tag>
```

Pull request and manual workflow builds do not push images.

## Secrets

The current CI build does not require custom GitHub secrets. It uses GitHub's built-in `GITHUB_TOKEN` to publish to GitHub Container Registry on pushes to `main`.

For production deployment, add these repository or environment secrets when the deployment target is known:

| Secret | Purpose |
| --- | --- |
| `DATABASE_URL` | Production PostgreSQL connection string |
| `AZURE_STORAGE_CONNECTION_STRING` | Production Azure Blob Storage connection string |
| `AZURE_STORAGE_CONTAINER_NAME` | Production Blob Storage container name |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins |
| `API_KEY` | Production API key for non-health endpoints |

Example commands:

```bash
gh secret set DATABASE_URL --repo tomasz-bec-lingaro/whse
gh secret set AZURE_STORAGE_CONNECTION_STRING --repo tomasz-bec-lingaro/whse
gh secret set AZURE_STORAGE_CONTAINER_NAME --repo tomasz-bec-lingaro/whse
gh secret set CORS_ALLOWED_ORIGINS --repo tomasz-bec-lingaro/whse
gh secret set API_KEY --repo tomasz-bec-lingaro/whse
```

Only run these commands with real values. Do not commit secrets to the repository.
