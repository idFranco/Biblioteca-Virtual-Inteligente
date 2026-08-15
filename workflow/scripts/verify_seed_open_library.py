"""Script one-off de verificación del seed del catálogo contra Open Library.

Lee el dataset ``workflow/backend/data/seed-books.json`` y, para cada libro,
invoca la tool ``ol_verify_by_isbn`` del MCP custom de Open Library por stdio
(reutilizando ``McpStdioClient`` del chatbot). El resultado se escribe en
``workflow/database/openlibrary_verification.json``.

Semántica (ADR-020): "disponible en Open Library" = la obra existe en OL y el
título devuelto coincide con el sembrado (comparación normalizada). NO implica
disponibilidad de préstamo. Si algún ISBN no se confirma, el libro se marca
``found: false`` para decisión humana: nunca se siembra una clave inventada.

Variables de entorno:
    SEED_BOOKS_FILE          ruta del dataset (por defecto
                             workflow/backend/data/seed-books.json)
    VERIFICATION_OUTPUT_FILE ruta de salida (por defecto
                             workflow/database/openlibrary_verification.json)
    OPEN_LIBRARY_MCP_COMMAND comando stdio del MCP (por defecto resuelve
                             workflow/mcp/open-library-mcp/server.py con el
                             intérprete actual)
    OL_VERIFY_SLEEP          segundos entre llamadas (por defecto 1.0; mínimo 1.0)
    OL_VERIFY_RETRIES        intentos por ISBN ante RuntimeError (por defecto 2)
    OL_VERIFY_RETRY_BACKOFF  segundos base del backoff entre reintentos (2.0)
    OL_VERIFY_TIMEOUT        timeout por llamada MCP en segundos (por defecto 30)

Uso:
    python workflow/scripts/verify_seed_open_library.py
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shlex
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- Resolución de rutas del monorepo (el script puede ejecutarse desde
# cualquier cwd: se resuelve la raíz del repo subiendo desde este archivo). ---
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
CHATBOT_DIR = REPO_ROOT / "workflow" / "chatbot"
if str(CHATBOT_DIR) not in sys.path:
    sys.path.insert(0, str(CHATBOT_DIR))

from app.mcp_clients.stdio import McpStdioClient  # noqa: E402

DEFAULT_SEED_FILE = REPO_ROOT / "workflow" / "backend" / "data" / "seed-books.json"
DEFAULT_OUTPUT_FILE = REPO_ROOT / "workflow" / "database" / "openlibrary_verification.json"
DEFAULT_MCP_SERVER = REPO_ROOT / "workflow" / "mcp" / "open-library-mcp" / "server.py"

VERIFY_SLEEP = max(1.0, float(os.getenv("OL_VERIFY_SLEEP", "1.0")))
VERIFY_RETRIES = max(1, int(os.getenv("OL_VERIFY_RETRIES", "2")))
VERIFY_RETRY_BACKOFF = float(os.getenv("OL_VERIFY_RETRY_BACKOFF", "2.0"))
MCP_CALL_TIMEOUT = float(os.getenv("OL_VERIFY_TIMEOUT", "30"))

# Estrategia empleada: verificación por ISBN exacto (schema de salida).
STRATEGY_ISBN = "isbn"


def _mcp_command() -> str:
    """Devuelve el comando stdio para lanzar el MCP de Open Library."""
    override = os.getenv("OPEN_LIBRARY_MCP_COMMAND")
    if override and override.strip():
        return override.strip()
    return f"{shlex.quote(sys.executable)} {shlex.quote(str(DEFAULT_MCP_SERVER))}"


def _load_seed_books(path: Path) -> list[dict[str, Any]]:
    """Carga el dataset de seed y devuelve la lista de libros.

    Soporta un JSON raíz en forma de lista o de objeto con una clave de lista
    (p. ej. ``{"books": [...]}``) para ser tolerante con el contrato final del
    dataset definido por el Backend Developer.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: si el JSON no contiene una lista de libros.
    """
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el dataset de seed: {path}")

    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)

    if isinstance(raw, list):
        books = raw
    elif isinstance(raw, dict):
        books = None
        for key, value in raw.items():
            if isinstance(key, str) and key.lower() == "books" and isinstance(value, list):
                books = value
                break
        if books is None:
            raise ValueError(f"El dataset {path} no contiene una lista de libros.")
    else:
        raise ValueError(f"El dataset {path} no es una lista de libros.")

    return [book for book in books if isinstance(book, dict)]


def _get_case_insensitive(mapping: dict[str, Any], key: str) -> Any:
    """Lee un campo ignorando mayúsculas (``Title``/``title``, ``Isbn``/``isbn``)."""
    for existing, value in mapping.items():
        if isinstance(existing, str) and existing.lower() == key.lower():
            return value
    return None


def _normalize_title(value: str) -> str:
    """Normaliza un título: minúsculas, sin acentos y con espacios colapsados."""
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


async def _call_verify(client: McpStdioClient, isbn: str) -> dict[str, Any]:
    """Invoca ``ol_verify_by_isbn`` vía MCP con timeout propio."""
    return await asyncio.wait_for(
        client.call_tool("ol_verify_by_isbn", {"isbn": isbn}),
        timeout=MCP_CALL_TIMEOUT,
    )


async def _verify_with_retry(client: McpStdioClient, isbn: str) -> dict[str, Any]:
    """Verifica un ISBN con reintentos y backoff ante errores transitorios.

    Nunca lanza: los fallos de red se devuelven como ``found: false`` con el
    error registrado para que el JSON documente el resultado por libro.
    """
    last_error: str | None = None
    for attempt in range(VERIFY_RETRIES):
        try:
            return await _call_verify(client, isbn)
        except (RuntimeError, asyncio.TimeoutError) as exc:
            last_error = str(exc)
            if attempt < VERIFY_RETRIES - 1:
                await asyncio.sleep(VERIFY_RETRY_BACKOFF * (2**attempt))

    return {
        "isbn": isbn,
        "found": False,
        "open_library_key": None,
        "title": None,
        "error": last_error or f"Fallo tras {VERIFY_RETRIES} intentos.",
    }


async def _verify_books(books: list[dict[str, Any]], command: str) -> list[dict[str, Any]]:
    """Verifica todos los libros del seed de forma serializada (rate limiting)."""
    client = McpStdioClient(command, name="open-library")
    results: list[dict[str, Any]] = []
    try:
        for index, book in enumerate(books):
            title = str(_get_case_insensitive(book, "title") or "").strip()
            author = str(_get_case_insensitive(book, "author") or "").strip()
            isbn = str(_get_case_insensitive(book, "isbn") or "").strip()

            if not isbn:
                results.append({
                    "title": title or None,
                    "author": author or None,
                    "isbn": None,
                    "found": False,
                    "open_library_key": None,
                    "matched_title": None,
                    "strategy": STRATEGY_ISBN,
                    "matched": False,
                    "error": "El libro del seed no tiene ISBN.",
                })
            else:
                verification = await _verify_with_retry(client, isbn)
                ol_title = verification.get("title") or None
                matched = bool(
                    verification.get("found")
                    and ol_title
                    and title
                    and _normalize_title(ol_title) == _normalize_title(title)
                )
                entry: dict[str, Any] = {
                    "title": title or None,
                    "author": author or None,
                    "isbn": verification.get("isbn") or isbn,
                    "found": bool(verification.get("found")),
                    "open_library_key": verification.get("open_library_key"),
                    "matched_title": ol_title,
                    "strategy": STRATEGY_ISBN,
                    "matched": matched,
                }
                if verification.get("error"):
                    entry["error"] = verification["error"]
                results.append(entry)

            if index < len(books) - 1:
                await asyncio.sleep(VERIFY_SLEEP)
    finally:
        await client.aclose()
    return results


def _write_output(results: list[dict[str, Any]], output_path: Path) -> None:
    """Escribe el JSON de verificación con el resumen agregado."""
    total = len(results)
    found = sum(1 for entry in results if entry["found"])
    matched = sum(1 for entry in results if entry["matched"])
    output = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "found": found,
            "not_found": total - found,
            "matched": matched,
        },
        "books": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)


def _print_summary(results: list[dict[str, Any]]) -> None:
    total = len(results)
    found = sum(1 for entry in results if entry["found"])
    matched = sum(1 for entry in results if entry["matched"])
    not_found = total - found
    print("Verificación del seed contra Open Library completada:")
    print(f"  Total:      {total}")
    print(f"  Encontrados: {found}")
    print(f"  No encontrados: {not_found}")
    print(f"  Títulos coincidentes: {matched}")
    for entry in results:
        if not entry["found"]:
            detail = entry.get("error") or "ISBN no indexado en Open Library"
            print(f"    - {entry.get('title')} (ISBN: {entry.get('isbn')}): {detail}")


def main() -> int:
    """Punto de entrada: verifica el seed y escribe el JSON de resultados."""
    seed_path = Path(os.getenv("SEED_BOOKS_FILE", str(DEFAULT_SEED_FILE))).resolve()
    output_path = Path(os.getenv("VERIFICATION_OUTPUT_FILE", str(DEFAULT_OUTPUT_FILE))).resolve()

    try:
        books = _load_seed_books(seed_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    results = asyncio.run(_verify_books(books, _mcp_command()))
    _write_output(results, output_path)

    print(f"Resultado escrito en: {output_path}")
    _print_summary(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
