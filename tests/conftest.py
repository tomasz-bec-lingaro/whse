import os
from collections.abc import Generator, Iterator

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("AZURE_STORAGE_CONNECTION_STRING", "UseDevelopmentStorage=true")
os.environ.setdefault("AZURE_STORAGE_CONTAINER_NAME", "test-documents")
os.environ.setdefault("API_KEY", "test-api-key")

from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_storage  # noqa: E402
from app.db import models  # noqa: F401, E402
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.rate_limit import upload_rate_limiter  # noqa: E402


class InMemoryStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}
        self.download_chunk_paths: list[str] = []

    def upload(self, path: str, data: bytes, content_type: str) -> None:
        self.files[path] = data

    def download(self, path: str) -> bytes:
        return b"".join(self.download_chunks(path))

    def download_chunks(self, path: str, chunk_size: int = 4) -> Iterator[bytes]:
        self.download_chunk_paths.append(path)
        data = self.files[path]

        def iter_chunks() -> Iterator[bytes]:
            for position in range(0, len(data), chunk_size):
                yield data[position : position + chunk_size]

        return iter_chunks()

    def delete(self, path: str) -> None:
        self.files.pop(path, None)


@pytest.fixture(autouse=True)
def database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def rate_limiter() -> Generator[None, None, None]:
    upload_rate_limiter.reset()
    yield
    upload_rate_limiter.reset()


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def client(storage: InMemoryStorage) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as test_client:
        test_client.headers.update({"X-API-Key": os.environ["API_KEY"]})
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def anonymous_client(storage: InMemoryStorage) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
