from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.errors import StorageOperationError


class AzureBlobStorage:
    def __init__(self, connection_string: str, container_name: str) -> None:
        self.container_name = container_name
        self.service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.service_client.get_container_client(container_name)
        self._ensure_container_exists()

    def _ensure_container_exists(self) -> None:
        try:
            self.container_client.create_container()
        except ResourceExistsError:
            return
        except Exception as exc:
            raise StorageOperationError("Blob Storage container cannot be initialized.") from exc

    def upload(self, path: str, data: bytes, content_type: str) -> None:
        try:
            self.container_client.upload_blob(
                name=path,
                data=data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )
        except Exception as exc:
            raise StorageOperationError("File upload to Blob Storage failed.") from exc

    def download(self, path: str) -> bytes:
        try:
            return self.container_client.download_blob(path).readall()
        except ResourceNotFoundError as exc:
            raise StorageOperationError("File was not found in Blob Storage.") from exc
        except Exception as exc:
            raise StorageOperationError("File download from Blob Storage failed.") from exc

    def delete(self, path: str) -> None:
        try:
            self.container_client.delete_blob(path)
        except ResourceNotFoundError:
            return
        except Exception as exc:
            raise StorageOperationError("File deletion from Blob Storage failed.") from exc
