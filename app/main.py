from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import require_whs_operator
from app.api.routers import deliveries, documents, health, suppliers, warehouses
from app.core.config import settings
from app.core.errors import StorageOperationError


def create_app() -> FastAPI:
    app = FastAPI(
        title="WHSE Delivery and Document Management API",
        description=(
            "WHS backend microservice for warehouse deliveries, suppliers, warehouses, "
            "and delivery document storage."
        ),
        version="0.1.0",
        openapi_tags=[
            {"name": "health", "description": "Service health checks."},
            {"name": "suppliers", "description": "Supplier management."},
            {"name": "warehouses", "description": "Warehouse management."},
            {"name": "deliveries", "description": "Warehouse delivery management."},
            {"name": "documents", "description": "Delivery document upload and download."},
        ],
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router, tags=["health"])
    protected_dependencies = [Depends(require_whs_operator)]
    app.include_router(
        suppliers.router,
        prefix="/suppliers",
        tags=["suppliers"],
        dependencies=protected_dependencies,
    )
    app.include_router(
        warehouses.router,
        prefix="/warehouses",
        tags=["warehouses"],
        dependencies=protected_dependencies,
    )
    app.include_router(
        deliveries.router,
        prefix="/deliveries",
        tags=["deliveries"],
        dependencies=protected_dependencies,
    )
    app.include_router(
        documents.router,
        prefix="/deliveries",
        tags=["documents"],
        dependencies=protected_dependencies,
    )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "The submitted data conflicts with existing records."},
        )

    @app.exception_handler(StorageOperationError)
    async def handle_storage_error(request: Request, exc: StorageOperationError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    return app


app = create_app()
