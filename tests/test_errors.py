"""One test per row of the errors table, and the error body contract."""
from datetime import date

import pytest


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_unknown_id_is_404(client, method):
    kwargs = {"json": {"title": "T", "author": "A"}} if method == "put" else {}
    r = getattr(client, method)("/books/42", **kwargs)
    assert r.status_code == 404
    assert list(r.json()) == ["detail"]


@pytest.mark.parametrize(
    "body",
    [
        {"author": "A"},                                         # title missing
        {"title": "T"},                                          # author missing
        {"title": "", "author": "A"},                            # title too short
        {"title": "x" * 201, "author": "A"},                     # title too long
        {"title": "T", "author": "x" * 101},                     # author too long
        {"title": 5, "author": "A"},                             # wrong type
        {"title": "T", "author": "A", "year": "1999"},           # wrong type
        {"title": "T", "author": "A", "year": -1},               # out of range
        {"title": "T", "author": "A", "year": date.today().year + 1},
        {"title": "T", "author": "A", "read": "yes"},            # wrong type
    ],
)
def test_invalid_book_is_422(client, body):
    r = client.post("/books", json=body)
    assert r.status_code == 422
    assert list(r.json()) == ["detail"]


def test_non_json_body_is_422(client):
    r = client.post("/books", content="not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert list(r.json()) == ["detail"]


def test_invalid_put_is_422(client, book):
    r = client.put(f"/books/{book['id']}", json={"title": "T"})
    assert r.status_code == 422