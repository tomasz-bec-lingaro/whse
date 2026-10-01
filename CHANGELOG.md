# Changelog

All notable changes to this project are documented in this file.

## HSE-008 - GitHub Actions coverage summary - 2026-10-01

- Added a GitHub Actions step that publishes pytest coverage to the job summary after tests.

## HSE-007 - CI workflow YAML fix - 2026-10-01

- Quoted GitHub Actions environment values containing colons so the workflow parser accepts the CI file before starting jobs.

## HSE-006 - Test suite refactor - 2026-10-01

- Split the long API flow test module into focused test modules by domain.
- Added shared test helpers for creating suppliers, warehouses, deliveries, and PDF documents.
- Reduced repeated setup code in document, delivery, auth, and WHS flow tests.
- Moved delivery business helpers from the delivery router into the service layer.
- Moved upload rate-limit dependency out of the document router into shared API dependencies.

## HSE-005 - Upload limits and Azurite CI - 2026-10-01

- Added in-memory per-client upload rate limiting for document uploads.
- Added a real Azurite integration test and a dedicated GitHub Actions job.
- Changed document soft delete to leave Blob Storage files untouched.
- Documented upload rate-limit configuration and soft-delete Blob Storage behavior.

## HSE-004 - Document storage resilience - 2026-10-01

- Streamed delivery-document downloads through storage chunk iterators instead of loading the whole file into memory.
- Added Blob Storage cleanup when metadata commit fails after a successful document upload.
- Configured local Azurite with the current default emulator key and API version check bypass required by newer Azure SDK requests.
- Added tests for chunked download behavior and upload cleanup on database commit failure.

## HSE-003 - Document I/O concurrency - 2026-10-01

- Aligned document upload, download, and delete handlers with FastAPI's worker threadpool model for blocking I/O.
- Kept synchronous SQLAlchemy and Azure Blob Storage calls out of the event loop by using regular FastAPI endpoints for document storage paths.
- Documented the current concurrency model and the future async database/storage migration path.

## HSE-002 - Security hardening - 2026-10-01

- Added API key authentication and WHS operator authorization dependency for non-health endpoints.
- Fixed direct delivery-document lookup so documents under soft-deleted deliveries are no longer downloadable or deletable.
- Removed internal `blob_path` from public delivery-document API responses.
- Added PDF/JPG magic-byte validation for document uploads.
- Restricted GitHub Actions image publishing to pushes on `main` and pinned workflow actions to commit SHAs.
- Pinned Docker images to manifest digests and added a non-root runtime user.
- Bound local PostgreSQL and Azurite Compose ports to `127.0.0.1`.
- Documented production API key, ingress, Azure Blob Storage, and CI publishing requirements.

## HSE-001 - Initial commit - 2026-10-01

- Added FastAPI backend for WHS delivery and document management.
- Added SQLAlchemy models for suppliers, warehouses, deliveries, and delivery documents.
- Added Alembic migrations with relationships, indexes, and soft-delete fields.
- Added REST endpoints for suppliers, warehouses, deliveries, and delivery documents.
- Added PDF/JPG upload, document listing, download, and Blob Storage metadata handling.
- Added Azure Blob Storage adapter with Azurite local emulator support.
- Added Dockerfile and Docker Compose for API, PostgreSQL, and Azurite.
- Added Poetry dependency management with `poetry.lock`.
- Added pytest API/service tests with coverage threshold.
- Added GitHub Actions CI with linting, format check, tests, Docker build, and GHCR publishing.
- Added README, production configuration, and GitHub setup documentation.
