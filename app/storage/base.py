from typing import Protocol


class BlobStorage(Protocol):
    def upload(self, path: str, data: bytes, content_type: str) -> None:
        pass

    def download(self, path: str) -> bytes:
        pass

    def delete(self, path: str) -> None:
        pass
