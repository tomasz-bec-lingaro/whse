# Changelog

All notable changes to this project are documented in this file.

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

