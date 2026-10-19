"""Reading-list CRUD API (Task 1 of the DevOps project)."""
from datetime import date
from typing import Annotated, Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr, field_validator

app = FastAPI(title="Reading List API")


class BookIn(BaseModel):
    """A book as the client sends it: no id. Strict types, so "1999" is not an int."""

    title: Annotated[StrictStr, Field(min_length=1, max_length=200)]
    author: Annotated[StrictStr, Field(min_length=1, max_length=100)]
    year: Optional[StrictInt] = None
    read: StrictBool = False

    @field_validator("year")
    @classmethod
    def year_in_range(cls, v):
        if v is not None and not 0 <= v <= date.today().year:
            raise ValueError(f"year must be between 0 and {date.today().year}")
        return v


class Book(BookIn):
    id: int


# Storage: TODO decide (in-memory for now; PostgreSQL from Task 8).
# Dicts keep insertion order, so listing is oldest first.
books: dict[int, Book] = {}
next_id = 1


def get_or_404(book_id: int) -> Book:
    if book_id not in books:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return books[book_id]


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(data: BookIn, response: Response):
    global next_id
    book = Book(id=next_id, **data.model_dump())
    books[book.id] = book
    next_id += 1  # never reused, even after a delete
    response.headers["Location"] = f"/books/{book.id}"
    return book


@app.get("/books", response_model=list[Book])
def list_books():
    return list(books.values())


@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    return get_or_404(book_id)


@app.put("/books/{book_id}", response_model=Book)
def replace_book(book_id: int, data: BookIn):
    get_or_404(book_id)
    # BookIn ignores an "id" in the body; missing year/read fall back to defaults.
    books[book_id] = Book(id=book_id, **data.model_dump())
    return books[book_id]


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    get_or_404(book_id)
    del books[book_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)