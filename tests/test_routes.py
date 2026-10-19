"""One test per row of the routes table."""


def test_create_book(client):
    r = client.post("/books", json={"title": "Dune", "author": "Frank Herbert", "year": 1965})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "title": "Dune", "author": "Frank Herbert", "year": 1965, "read": False}
    assert r.headers["Location"] == "/books/1"


def test_list_books_oldest_first(client):
    assert client.get("/books").json() == []
    client.post("/books", json={"title": "A", "author": "X"})
    client.post("/books", json={"title": "B", "author": "Y"})
    r = client.get("/books")
    assert r.status_code == 200
    assert [b["title"] for b in r.json()] == ["A", "B"]


def test_read_book(client, book):
    r = client.get(f"/books/{book['id']}")
    assert r.status_code == 200
    assert r.json() == book


def test_replace_book_resets_defaults_and_ignores_id(client):
    client.post("/books", json={"title": "Dune", "author": "Frank Herbert", "year": 1965, "read": True})
    r = client.put("/books/1", json={"id": 99, "title": "Dune Messiah", "author": "Frank Herbert"})
    assert r.status_code == 200
    assert r.json() == {"id": 1, "title": "Dune Messiah", "author": "Frank Herbert", "year": None, "read": False}
    assert client.get("/books/1").json() == r.json()


def test_delete_book_and_id_not_reused(client, book):
    r = client.delete(f"/books/{book['id']}")
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(f"/books/{book['id']}").status_code == 404
    new = client.post("/books", json={"title": "Emma", "author": "Jane Austen"}).json()
    assert new["id"] != book["id"]


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}