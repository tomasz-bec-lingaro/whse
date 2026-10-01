from functools import lru_cache

from app.core.config import settings
from app.storage.azure_blob import AzureBlobStorage
from app.storage.base import BlobStorage


@lru_cache
def get_storage_client() -> BlobStorage:
    return AzureBlobStorage(
        connection_string=settings.azure_storage_connection_string,
        container_name=settings.azure_storage_container_name,
    )


def get_storage() -> BlobStorage:
    return get_storage_client()
