import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client():
    main.books.clear()
    main.next_id = 1
    return TestClient(main.app)


@pytest.fixture
def book(client):
    return client.post("/books", json={"title": "Dune", "author": "Frank Herbert", "year": 1965}).json()