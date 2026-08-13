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


async def _get_json(path: str, client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    """Descarga y decodifica un JSON de Open Library.

    Args:
        path: ruta (con query string) relativa a ``OPEN_LIBRARY_BASE_URL``.
        client: cliente ``httpx.AsyncClient`` opcional. En producción se crea
            uno por llamada con el timeout configurado; los tests inyectan un
            cliente con ``httpx.MockTransport``.

    Returns:
        El JSON decodificado. Lanza ``httpx.HTTPError`` si la petición falla.
    """
    if client is None:
        async with httpx.AsyncClient(timeout=OPEN_LIBRARY_TIMEOUT) as default_client:
            return await _get_json(path, default_client)

    response = await client.get(
        f"{OPEN_LIBRARY_BASE_URL}{path}",
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()


def _extract_edition_key(entry: Any) -> str | None:
    """Extrae la clave de edición (OLID) de una entrada de ``/api/books``.

    Con ``jscmd=data`` la respuesta mapea cada bibkey a un dict con el campo
    ``key`` (``/books/OL...``), el identificador ``openlibrary`` en
    ``identifiers`` y, en algunos formatos, una lista ``keys``. Se devuelve la
    clave en formato de ruta (p. ej. ``/books/OL7353617M``) para que sea
    directamente consumible por ``ol_get_book_details``.

    Returns:
        La clave OLID de la edición o ``None`` si no se puede determinar.
    """
    if not isinstance(entry, dict):
        return None

    key = entry.get("key")
    if isinstance(key, str) and key.strip():
        return key.strip()

    identifiers = entry.get("identifiers")
    if isinstance(identifiers, dict):
        ol_ids = identifiers.get("openlibrary")
        if isinstance(ol_ids, list) and ol_ids and isinstance(ol_ids[0], str):
            olid = ol_ids[0].strip()
            if olid:
                return olid if olid.startswith("/") else f"/books/{olid}"

    keys = entry.get("keys")
    if isinstance(keys, list):
        for candidate in keys:
            if isinstance(candidate, str) and candidate.strip():
                candidate = candidate.strip()
                if candidate.startswith("/books/") or candidate.startswith("OL"):
                    return candidate if candidate.startswith("/") else f"/books/{candidate}"

    return None


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


@mcp.tool()
async def ol_verify_by_isbn(isbn: str) -> dict[str, Any]:
    """Verifica si un ISBN existe en Open Library y devuelve su clave de edición.

    Consulta ``/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data``, el
    endpoint de libros por identificador exacto. Si Open Library no indexa el
    ISBN, devuelve ``found: false`` sin lanzar error: la verificación documenta
    el resultado sin inventar datos.

    Args:
        isbn: ISBN-10 o ISBN-13 del libro a verificar.

    Returns:
        Dict con ``isbn`` (entrada normalizada), ``found`` (bool),
        ``open_library_key`` (clave OLID de la edición o null) y ``title``
        (título indexado por Open Library o null). Lanza RuntimeError con
        mensaje estructurado si Open Library no responde.
    """
    return await _verify_by_isbn(isbn)


async def _verify_by_isbn(isbn: str, client: httpx.AsyncClient | None = None) -> dict[str, Any]:
    """Implementación de ``ol_verify_by_isbn`` (cliente inyectable en tests)."""
    normalized_isbn = isbn.strip() if isinstance(isbn, str) else ""
    if not normalized_isbn:
        raise ValueError("El ISBN no puede estar vacío.")

    path = f"/api/books?bibkeys=ISBN:{normalized_isbn}&format=json&jscmd=data"
    try:
        data = await _get_json(path, client)
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Open Library no respondió al verificar el ISBN '{normalized_isbn}': {exc}"
        ) from exc

    if not isinstance(data, dict):
        return {
            "isbn": normalized_isbn,
            "found": False,
            "open_library_key": None,
            "title": None,
        }

    entry = data.get(f"ISBN:{normalized_isbn}")
    if entry is None:
        # Open Library normaliza el bibkey (p. ej. elimina guiones del ISBN);
        # se recorre la respuesta para localizar la única entrada ISBN:...
        for bibkey, candidate in data.items():
            if isinstance(bibkey, str) and bibkey.startswith("ISBN:") and isinstance(candidate, dict):
                entry = candidate
                break

    if entry is None or not isinstance(entry, dict):
        # La respuesta vacía ({}) indica que el ISBN no está indexado.
        return {
            "isbn": normalized_isbn,
            "found": False,
            "open_library_key": None,
            "title": None,
        }

    return {
        "isbn": normalized_isbn,
        "found": True,
        "open_library_key": _extract_edition_key(entry),
        "title": _extract_text(entry.get("title")),
    }


if __name__ == "__main__":
    mcp.run()
