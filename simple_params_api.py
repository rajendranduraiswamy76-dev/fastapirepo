from typing import Any

from fastapi import Body, FastAPI, HTTPException, Response, status

app = FastAPI(title="Library Book API (Simple Parameters)")

# In-memory storage. Restarting the app resets this data.
books_db: dict[int, dict[str, Any]] = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "available": True},
    2: {"id": 2, "title": "The Pragmatic Programmer", "author": "Andy Hunt", "year": 1999, "available": False},
}
next_book_id = 3


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Library Book API (Simple Parameters) is running"}


@app.get("/books")
def list_books() -> list[dict[str, Any]]:
    return list(books_db.values())


@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict[str, Any]:
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(
    title: str = Body(..., min_length=1),
    author: str = Body(..., min_length=1),
    year: int = Body(..., ge=0),
    available: bool = Body(True),
) -> dict[str, Any]:
    global next_book_id

    book = {
        "id": next_book_id,
        "title": title,
        "author": author,
        "year": year,
        "available": available,
    }
    books_db[next_book_id] = book
    next_book_id += 1
    return book


@app.put("/books/{book_id}")
def replace_book(
    book_id: int,
    title: str = Body(..., min_length=1),
    author: str = Body(..., min_length=1),
    year: int = Body(..., ge=0),
    available: bool = Body(True),
) -> dict[str, Any]:
    if book_id not in books_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    updated_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "year": year,
        "available": available,
    }
    books_db[book_id] = updated_book
    return updated_book


@app.patch("/books/{book_id}")
def update_book(
    book_id: int,
    title: str | None = Body(default=None, min_length=1),
    author: str | None = Body(default=None, min_length=1),
    year: int | None = Body(default=None, ge=0),
    available: bool | None = Body(default=None),
) -> dict[str, Any]:
    existing = books_db.get(book_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if title is not None:
        existing["title"] = title
    if author is not None:
        existing["author"] = author
    if year is not None:
        existing["year"] = year
    if available is not None:
        existing["available"] = available

    return existing


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int) -> Response:
    if book_id not in books_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    del books_db[book_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)