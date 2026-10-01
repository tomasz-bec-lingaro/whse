from dataclasses import dataclass
from functools import lru_cache
from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.services.rate_limit import upload_rate_limiter
from app.storage.azure_blob import AzureBlobStorage
from app.storage.base import BlobStorage

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass(frozen=True)
class Principal:
    subject: str
    roles: frozenset[str]


@lru_cache
def get_storage_client() -> BlobStorage:
    return AzureBlobStorage(
        connection_string=settings.azure_storage_connection_string,
        container_name=settings.azure_storage_container_name,
    )


def get_storage() -> BlobStorage:
    return get_storage_client()


def get_current_principal(
    api_key: Annotated[str | None, Security(api_key_header)],
) -> Principal:
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication is not configured.",
        )
    if api_key is None or not compare_digest(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return Principal(subject="api-key", roles=settings.api_roles)


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]


def require_whs_operator(principal: CurrentPrincipal) -> Principal:
    if "whs:operator" not in principal.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
    return principal


def _client_rate_limit_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip()
    if request.client is None:
        return "unknown"
    return request.client.host


def enforce_upload_rate_limit(request: Request) -> None:
    allowed, retry_after = upload_rate_limiter.allow(
        key=_client_rate_limit_key(request),
        limit=settings.upload_rate_limit_per_minute,
        window_seconds=settings.upload_rate_limit_window_seconds,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Upload rate limit exceeded.",
            headers={"Retry-After": str(retry_after)},
        )
