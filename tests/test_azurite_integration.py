import os
from uuid import uuid4

import pytest

from app.storage.azure_blob import AzureBlobStorage


@pytest.mark.skipif(
    os.environ.get("RUN_AZURITE_INTEGRATION") != "1",
    reason="Azurite integration test is opt-in.",
)
def test_azure_blob_storage_with_real_azurite() -> None:
    container_name = f"test-documents-{uuid4().hex[:12]}"
    storage = AzureBlobStorage(
        connection_string=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
        container_name=container_name,
    )
    blob_path = "deliveries/1/documents/1/integration.pdf"
    content = b"%PDF-1.4 azurite integration"

    try:
        storage.upload(blob_path, content, "application/pdf")

        downloaded = b"".join(storage.download_chunks(blob_path, chunk_size=4))
        assert downloaded == content

        storage.delete(blob_path)
    finally:
        storage.container_client.delete_container()
