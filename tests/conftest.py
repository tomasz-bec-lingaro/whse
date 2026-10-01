import os
from collections.abc import Generator

import pytest

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "UseDevelopmentStorage=true"
os.environ["AZURE_STORAGE_CONTAINER_NAME"] = "test-documents"

from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_storage  # noqa: E402
from app.db import models  # noqa: F401, E402
from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


class InMemoryStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    def upload(self, path: str, data: bytes, content_type: str) -> None:
        self.files[path] = data

    def download(self, path: str) -> bytes:
        return self.files[path]

    def delete(self, path: str) -> None:
        self.files.pop(path, None)


@pytest.fixture(autouse=True)
def database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def client(storage: InMemoryStorage) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
