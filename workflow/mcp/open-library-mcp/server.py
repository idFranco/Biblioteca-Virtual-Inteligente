import os
from typing import Any

import httpx
from fastmcp import FastMCP

OPEN_LIBRARY_BASE_URL = os.getenv("OPEN_LIBRARY_BASE_URL", "https://openlibrary.org")
OPEN_LIBRARY_TIMEOUT = float(os.getenv("OPEN_LIBRARY_TIMEOUT", "10"))
SEARCH_LIMIT = int(os.getenv("OPEN_LIBRARY_SEARCH_LIMIT", "5"))

mcp = FastMCP("open-library")


def _extract_text(value: Any) -> str | None:
    """Devuelve el texto de un campo que puede ser ``str`` o dict ``{"value": ...}``."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and value.get("value"):
        return str(value["value"])
    return None


def _build_cover_url(cover_id: int | None, size: str = "M") -> str | None:
    if cover_id is None:
        return None
    return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"


async def _get_json(path: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=OPEN_LIBRARY_TIMEOUT) as client:
        response = await client.get(
            f"{OPEN_LIBRARY_BASE_URL}{path}",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def ol_search_books(query: str, limit: int = SEARCH_LIMIT) -> list[dict[str, Any]]:
    """Busca libros en Open Library por título, autor o ISBN.

    Args:
        query: texto de búsqueda (título, autor o ISBN).
        limit: número máximo de resultados (1-20).

    Returns:
        Lista de resultados con title, author, isbn, key (OLID), cover y
        first_publish_year.
    """
    if not query or not query.strip():
        return []
    normalized_limit = max(1, min(limit, 20))

    try:
        params = httpx.QueryParams({"q": query, "limit": str(normalized_limit)})
        data = await _get_json(f"/search.json?{params}")
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Open Library no respondió: {exc}") from exc

    results: list[dict[str, Any]] = []
    for doc in data.get("docs", []):
        author = None
        if doc.get("author_name"):
            author = doc["author_name"][0]

        isbn = None
        if doc.get("isbn"):
            isbn = doc["isbn"][0]

        key = doc.get("key")
        cover_id = doc.get("cover_i")

        results.append({
            "title": doc.get("title"),
            "author": author,
            "isbn": isbn,
            "key": key,
            "first_publish_year": doc.get("first_publish_year"),
            "cover_url": _build_cover_url(cover_id),
        })

    return results


@mcp.tool()
async def ol_get_book_details(key: str) -> dict[str, Any]:
    """Obtiene el detalle bibliográfico de una obra de Open Library.

    Args:
        key: clave de la obra en formato ``/works/OL...W`` o ``OL...W``.

    Returns:
        Dict con title, author, key, isbn, genre/subjects, description y
        cover_url. Lanza RuntimeError si Open Library no responde.
    """
    normalized_key = key if key.startswith("/") else f"/{key}"

    try:
        work = await _get_json(f"{normalized_key}.json")
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Open Library no respondió para '{key}': {exc}") from exc

    author_name = None
    author_keys = work.get("authors") or []
    if author_keys:
        author_url = author_keys[0].get("author", {}).get("key")
        if author_url:
            try:
                author_data = await _get_json(f"{author_url}.json")
                author_name = author_data.get("name")
            except httpx.HTTPError:
                author_name = None

    subjects = work.get("subjects") or []
    description = _extract_text(work.get("description"))

    covers = work.get("covers") or []
    cover_url = _build_cover_url(covers[0]) if covers else None

    isbn_13 = work.get("isbn_13") or []
    isbn_10 = work.get("isbn_10") or []
    isbn = (isbn_13 or isbn_10 or [None])[0]

    return {
        "key": normalized_key,
        "title": work.get("title"),
        "author": author_name,
        "genre": ", ".join(subjects[:5]) if subjects else None,
        "description": description,
        "cover_url": cover_url,
        "isbn": isbn,
    }


if __name__ == "__main__":
    mcp.run()
