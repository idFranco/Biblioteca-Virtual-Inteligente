import sys
from pathlib import Path

from fastmcp import FastMCP

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


@mcp.tool()
def consultar_alquileres_usuario(user_id: str) -> list[dict]:
    """Devuelve el historial de alquileres de un usuario.

    Args:
        user_id: identificador del usuario.

    Returns:
        Lista de alquileres con book_id, title, rented_at, due_date,
        returned_at y status. Lista vacía si no hay historial.
    """
    try:
        rows = _db().query(
            "SELECT r.Id, r.BookId, b.Title, r.RentedAt, r.DueDate, "
            "r.ReturnedAt, r.Status "
            "FROM Rentals r JOIN Books b ON b.Id = r.BookId "
            "WHERE r.UserId = ? ORDER BY r.RentedAt DESC",
            [user_id],
        )
    except Exception:
        return []

    return [
        {
            "id": row[0],
            "book_id": row[1],
            "title": row[2],
            "rented_at": row[3],
            "due_date": row[4],
            "returned_at": row[5],
            "status": row[6],
        }
        for row in rows
    ]


@mcp.tool()
def consultar_libro_en_curso(user_id: str) -> dict | None:
    """Devuelve el libro que el usuario tiene alquilado actualmente, si existe.

    Args:
        user_id: identificador del usuario.

    Returns:
        dict con book_id, title, due_date y status del alquiler activo,
        o None si el usuario no tiene ningún alquiler en curso.
    """
    try:
        rows = _db().query(
            "SELECT r.Id, r.BookId, b.Title, r.DueDate, r.Status "
            "FROM Rentals r JOIN Books b ON b.Id = r.BookId "
            "WHERE r.UserId = ? AND r.Status = 'Active' "
            "ORDER BY r.RentedAt DESC LIMIT 1",
            [user_id],
        )
    except Exception:
        return None

    if not rows:
        return None
    return {
        "id": rows[0][0],
        "book_id": rows[0][1],
        "title": rows[0][2],
        "due_date": rows[0][3],
        "status": rows[0][4],
    }


@mcp.tool()
def obtener_preferencias(user_id: str) -> list[dict]:
    """Devuelve las preferencias de género guardadas por un usuario.

    Args:
        user_id: identificador del usuario.

    Returns:
        Lista de preferencias con genre y created_at. Lista vacía si no hay.
    """
    try:
        rows = _db().query(
            "SELECT Id, Genre, CreatedAt FROM UserPreferences "
            "WHERE UserId = ? ORDER BY CreatedAt DESC",
            [user_id],
        )
    except Exception:
        return []

    return [
        {"id": row[0], "genre": row[1], "created_at": row[2]}
        for row in rows
    ]


@mcp.tool()
def listar_recomendaciones_por_genero(user_id: str, limit: int = 5) -> list[dict]:
    """Recomienda libros disponibles según los géneros del historial y preferencias.

    Args:
        user_id: identificador del usuario.
        limit: número máximo de recomendaciones (1-20).

    Returns:
        Lista de libros disponibles con id, title, author, genre,
        available_copies y un campo `reason` con el origen de la recomendación.
    """
    normalized_limit = max(1, min(limit, 20))
    try:
        genres = _db().query(
            "SELECT DISTINCT b.Genre FROM Rentals r "
            "JOIN Books b ON b.Id = r.BookId WHERE r.UserId = ? "
            "AND b.Genre IS NOT NULL AND b.Genre <> ''",
            [user_id],
        )
        preferred = _db().query(
            "SELECT Genre FROM UserPreferences WHERE UserId = ?",
            [user_id],
        )
    except Exception:
        return []

    genre_values = {row[0] for row in [*genres, *preferred] if row[0]}
    if not genre_values:
        return []

    placeholders = ",".join("?" for _ in genre_values)
    try:
        rows = _db().query(
            f"SELECT Id, Title, Author, Genre, AvailableCopies "
            f"FROM Books WHERE Genre IN ({placeholders}) "
            f"AND AvailableCopies > 0 "
            f"ORDER BY Title LIMIT {normalized_limit}",
            list(genre_values),
        )
    except Exception:
        return []

    preferred_set = {row[0] for row in preferred if row[0]}
    return [
        {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "genre": row[3],
            "available_copies": row[4],
            "reason": (
                "coincide con tus preferencias"
                if row[3] in preferred_set
                else "coincide con tu historial de lectura"
            ),
        }
        for row in rows
    ]


@mcp.tool()
def registrar_feedback(user_id: str, book_id: str, rating: int, comment: str | None = None) -> dict:
    """Registra el feedback de un usuario sobre un libro.

    Args:
        user_id: identificador del usuario.
        book_id: identificador del libro.
        rating: puntuación de 1 a 5.
        comment: comentario opcional del usuario.

    Returns:
        dict con success, id y un mensaje de confirmación.
        Si la base de datos no está disponible devuelve success=False.
    """
    normalized_rating = max(1, min(rating, 5))
    try:
        book_exists = _db().query(
            "SELECT Id FROM Books WHERE Id = ?", [book_id]
        )
    except Exception:
        return {"success": False, "reason": "La base de datos no está disponible."}

    if not book_exists:
        return {"success": False, "reason": "El libro no existe en el catálogo."}

    try:
        feedback_id = _db().query(
            "SELECT lower(hex(randomblob(16)))", []
        )[0][0]
        _db().execute(
            "INSERT INTO Feedback (Id, UserId, BookId, Rating, Comment, CreatedAt) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
            [feedback_id, user_id, book_id, normalized_rating, comment],
        )
    except Exception:
        return {"success": False, "reason": "No se pudo registrar el feedback."}

    return {
        "success": True,
        "id": feedback_id,
        "message": "Gracias por tu valoración.",
    }


if __name__ == "__main__":
    mcp.run()
