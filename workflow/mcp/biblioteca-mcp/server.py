import sys
from pathlib import Path

from mcp.server import FastMCP

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "workflow" / "mcp"))

from common.settings import get_database_path
from common.sqlite import DbAccess

mcp = FastMCP("Biblioteca-MCP")

DB_PATH = get_database_path()


def _db() -> DbAccess:
    return DbAccess(DB_PATH)


@mcp.tool()
def ping() -> str:
    return "pong"


@mcp.tool()
def buscar_libros(search: str | None = None, limit: int = 10) -> list[dict]:
    """Busca libros en el catálogo interno leyendo la base de datos SQLite.

    Args:
        search: texto para filtrar por título o autor (opcional).
        limit: número máximo de resultados (1-100).

    Returns:
        Lista de libros con id, title, author, isbn, genre y available_copies.
        Devuelve una lista vacía si la base de datos no existe o no hay resultados.
    """
    normalized_limit = max(1, min(limit, 100))
    sql = (
        "SELECT Id, Title, Author, Isbn, Genre, AvailableCopies "
        "FROM Books"
    )
    params: list[object] = []
    if search:
        sql += " WHERE LOWER(Title) LIKE ? OR LOWER(Author) LIKE ?"
        pattern = f"%{search.lower()}%"
        params = [pattern, pattern]
    sql += f" ORDER BY Title LIMIT {normalized_limit}"

    try:
        rows = _db().query(sql, params)
    except Exception:
        return []

    return [
        {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "isbn": row[3],
            "genre": row[4],
            "available_copies": row[5],
        }
        for row in rows
    ]


@mcp.tool()
def verificar_disponibilidad(book_id: str) -> dict:
    """Devuelve la disponibilidad actual de un libro por su id."""
    try:
        rows = _db().query(
            "SELECT Title, TotalCopies, AvailableCopies, Status FROM Books WHERE Id = ?",
            [book_id],
        )
    except Exception:
        return {"found": False, "reason": "La base de datos no está disponible."}

    if not rows:
        return {"found": False}
    title, total, available, status = rows[0]
    return {
        "found": True,
        "book_id": book_id,
        "title": title,
        "total_copies": total,
        "available_copies": available,
        "status": status,
        "is_available": available > 0,
    }


@mcp.tool()
def get_estado_lectura(user_id: str) -> dict:
    """Devuelve el estado de lectura de un usuario según sus alquileres activos.

    Valores: sin_actividad, en_curso, por_vencer (a <2 días), vencido,
    recien_devuelto (devolución en los últimos 14 días).
    """
    try:
        active = _db().query(
            "SELECT DueDate FROM Rentals WHERE UserId = ? AND Status = 'Active'",
            [user_id],
        )
    except Exception:
        return {"user_id": user_id, "estado": "sin_actividad"}

    if not active:
        return {"user_id": user_id, "estado": "sin_actividad"}

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    for (due_date,) in active:
        due = _parse_date(due_date)
        if due is None:
            continue
        if due < now:
            return {"user_id": user_id, "estado": "vencido"}
        if (due - now).days <= 2:
            return {"user_id": user_id, "estado": "por_vencer"}

    return {"user_id": user_id, "estado": "en_curso"}


def _parse_date(value: object):
    from datetime import datetime, timezone

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if hasattr(value, "astimezone"):
        return value.astimezone(timezone.utc)
    return value


if __name__ == "__main__":
    mcp.run()
