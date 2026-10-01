# HSE Microservice - Delivery and Document Management

Backend microservice for the WHS system responsible for warehouse delivery management, delivery document metadata, and file handling through Blob Storage.

WHS means Warehouse System in this project context.

## Recommended Tech Stack

| Area | Technology | Reason |
| --- | --- | --- |
| Language | Python 3.12 | Modern Python runtime with strong ecosystem support |
| Web framework | FastAPI | Native OpenAPI generation, Pydantic validation, async support |
| API validation | Pydantic v2 | Strong request/response models and examples |
| ORM | SQLAlchemy 2.x | Mature ORM with explicit relationship and query support |
| Migrations | Alembic | Standard migration tooling for SQLAlchemy |
| Database | PostgreSQL | Production-ready relational database for WHS data |
| Local database | SQLite or PostgreSQL via Docker | Lightweight local option or production-like local stack |
| Blob Storage | Azure Blob Storage | Managed object storage for delivery documents |
| Local storage | Azurite or filesystem adapter | Local development without storing files in the repository |
| Dependency manager | Poetry | Reproducible installs through `poetry.lock` |
| Testing | pytest, pytest-cov, httpx | Unit tests, API tests, and coverage reporting |
| Linting/formatting | Ruff | Fast linting and formatting with one tool |
| Containerization | Docker, Docker Compose | Single-command local startup with app and database |
| CI/CD | GitHub Actions | PR-triggered checks, Docker image build, and artifact publishing |
| Documentation | OpenAPI/Swagger, README | Automatic API documentation plus project usage docs |

## Documentation

Production configuration is described in [docs/production-configuration.md](docs/production-configuration.md).

GitHub repository setup is described in [docs/github-setup.md](docs/github-setup.md).

## Local Startup With Docker Compose

Start the full local stack:

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Azurite Blob Storage emulator: `localhost:10000`

The API container runs Alembic migrations before starting the FastAPI server.

## Environment Variables

Use `.env.example` as the template for local configuration.

Required variables:

- `APP_ENV`
- `LOG_LEVEL`
- `DATABASE_URL`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_STORAGE_CONTAINER_NAME`
- `MAX_UPLOAD_SIZE_MB`
- `CORS_ALLOWED_ORIGINS`

Do not commit real secrets to the repository.

For production, use `.env.production.example` as a template and inject real values through the deployment platform secret store.

## Local Development Without Docker

Install dependencies:

```bash
poetry install
```

Create or update the lockfile:

```bash
poetry lock
```

Run migrations:

```bash
poetry run alembic upgrade head
```

Start the API:

```bash
poetry run uvicorn app.main:app --reload
```

Run checks:

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
```

## Example WHS Flow

1. Create a supplier with `POST /suppliers`.
2. Create a warehouse with `POST /warehouses`.
3. Create a delivery with `POST /deliveries`.
4. Upload a PDF or JPG document with `POST /deliveries/{delivery_id}/documents`.
5. List documents with `GET /deliveries/{delivery_id}/documents`.
6. Download a document with `GET /deliveries/{delivery_id}/documents/{document_id}/download`.
7. Change delivery status with `PATCH /deliveries/{delivery_id}/status`.

## Implemented MVP Scope

- FastAPI application with generated OpenAPI/Swagger docs.
- PostgreSQL persistence with SQLAlchemy models and Alembic migration.
- CRUD endpoints for suppliers, warehouses, and deliveries.
- Delivery document upload, list, download, and soft delete.
- Azure Blob Storage adapter compatible with Azurite for local development.
- Dockerfile and Docker Compose for local startup.
- pytest API and service tests.
- GitHub Actions workflow for linting, tests, coverage, and Docker build.
- GitHub Actions image publishing to GitHub Container Registry on `main`.
