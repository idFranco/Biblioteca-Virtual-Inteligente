"""Tests de las herramientas de Biblioteca-MCP para el flujo de recomendación.

Usa una base SQLite temporal en disco para verificar consultas reales y el
escenario de base de datos no disponible (ruta inexistente).
"""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
MCP_DIR = REPO_ROOT / "workflow" / "mcp"
SERVER_DIR = MCP_DIR / "biblioteca-mcp"
for path in (str(MCP_DIR), str(SERVER_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    database = tmp_path / "biblioteca_test.db"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE Books (
            Id TEXT PRIMARY KEY,
            Title TEXT NOT NULL,
            Author TEXT NOT NULL,
            Isbn TEXT,
            Genre TEXT,
            Description TEXT,
            OpenLibraryKey TEXT,
            TotalCopies INTEGER NOT NULL DEFAULT 0,
            AvailableCopies INTEGER NOT NULL DEFAULT 0,
            Status TEXT NOT NULL DEFAULT 'Available',
            CreatedAt TEXT,
            UpdatedAt TEXT
        );
        CREATE TABLE Rentals (
            Id TEXT PRIMARY KEY,
            UserId TEXT NOT NULL,
            BookId TEXT NOT NULL,
            RentedAt TEXT,
            DueDate TEXT,
            ReturnedAt TEXT,
            Status TEXT NOT NULL DEFAULT 'Active'
        );
        CREATE TABLE UserPreferences (
            Id TEXT PRIMARY KEY,
            UserId TEXT NOT NULL,
            Genre TEXT NOT NULL,
            CreatedAt TEXT
        );
        CREATE TABLE Feedbacks (
            Id TEXT PRIMARY KEY,
            UserId TEXT NOT NULL,
            BookId TEXT NOT NULL,
            Rating INTEGER NOT NULL,
            Comment TEXT,
            CreatedAt TEXT
        );
        """
    )
    connection.executemany(
        "INSERT INTO Books (Id, Title, Author, Genre, AvailableCopies, TotalCopies) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("b1", "Cien años de soledad", "García Márquez", "Novela", 2, 3),
            ("b2", "Rayuela", "Cortázar", "Novela", 0, 1),
            ("b3", "Sapiens", "Harari", "Historia", 5, 5),
            ("b4", "El principito", "Saint-Exupéry", "Infantil", 1, 2),
        ],
    )
    connection.execute(
        "INSERT INTO Rentals (Id, UserId, BookId, RentedAt, DueDate, Status) "
        "VALUES ('r1', 'user-1', 'b1', '2026-07-01', '2026-08-20', 'Active')"
    )
    connection.execute(
        "INSERT INTO Rentals (Id, UserId, BookId, RentedAt, DueDate, ReturnedAt, Status) "
        "VALUES ('r2', 'user-1', 'b3', '2026-06-01', '2026-06-15', '2026-06-14', 'Returned')"
    )
    connection.execute(
        "INSERT INTO UserPreferences (Id, UserId, Genre, CreatedAt) "
        "VALUES ('p1', 'user-1', 'Historia', '2026-08-01')"
    )
    connection.commit()
    connection.close()
    return database


@pytest.fixture()
def server(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    from common.settings import clear_settings_cache

    clear_settings_cache()
    import importlib
    import server as server_module

    importlib.reload(server_module)
    server_module.DB_PATH = server_module.get_database_path()
    yield server_module


def test_consultar_alquileres_usuario(server):
    result = server.consultar_alquileres_usuario("user-1")
    assert len(result) == 2
    assert result[0]["book_id"] == "b1"
    assert result[0]["status"] == "Active"
    assert {item["book_id"] for item in result} == {"b1", "b3"}


def test_consultar_alquileres_usuario_vacio(server):
    assert server.consultar_alquileres_usuario("sin-alquileres") == []


def test_consultar_libro_en_curso(server):
    result = server.consultar_libro_en_curso("user-1")
    assert result is not None
    assert result["book_id"] == "b1"
    assert result["title"] == "Cien años de soledad"
    assert result["status"] == "Active"


def test_consultar_libro_en_curso_sin_alquiler(server):
    assert server.consultar_libro_en_curso("otro-usuario") is None


def test_consultar_alquileres_insensible_al_case(server):
    """El contrato userId es case-insensitive: USER-1 == user-1."""
    lower = server.consultar_alquileres_usuario("user-1")
    upper = server.consultar_alquileres_usuario("USER-1")
    assert {item["book_id"] for item in upper} == {"b1", "b3"}
    assert [r["book_id"] for r in upper] == [r["book_id"] for r in lower]


def test_recomendaciones_insensibles_al_case(server):
    """USER-1 (mayúsculas) debe recomendar igual que user-1 (minúsculas)."""
    lower = server.listar_recomendaciones_por_genero("user-1", limit=5)
    upper = server.listar_recomendaciones_por_genero("USER-1", limit=5)
    assert {item["id"] for item in upper} == {"b1", "b3"}
    assert {item["id"] for item in upper} == {item["id"] for item in lower}
    assert len(upper) == len(lower)


def test_obtener_preferencias(server):
    result = server.obtener_preferencias("user-1")
    assert len(result) == 1
    assert result[0]["genre"] == "Historia"


def test_obtener_preferencias_vacio(server):
    assert server.obtener_preferencias("sin-preferencias") == []


def test_listar_recomendaciones_por_genero(server):
    """user-1 alquiló Novela e Historia y prefiere Historia."""
    result = server.listar_recomendaciones_por_genero("user-1", limit=5)
    genres = {item["genre"] for item in result}
    assert "Novela" in genres or "Historia" in genres
    # Solo libros disponibles (Rayuela tiene 0 copias y se excluye)
    assert all(int(item["available_copies"]) > 0 for item in result)
    assert {item["id"] for item in result} == {"b1", "b3"}


def test_listar_recomendaciones_sin_historial(server):
    assert server.listar_recomendaciones_por_genero("nuevo-usuario", limit=5) == []


def test_registrar_feedback(server):
    result = server.registrar_feedback("user-1", "b1", 5, "Excelente")
    assert result["success"] is True
    assert result["id"]

    rows = sqlite3.connect(str(server.DB_PATH)).execute(
        "SELECT Rating, Comment FROM Feedbacks WHERE UserId = 'user-1' AND BookId = 'b1'"
    ).fetchall()
    assert rows == [(5, "Excelente")]


def test_registrar_feedback_clamps_rating(server):
    result = server.registrar_feedback("user-1", "b1", 99)
    assert result["success"] is True
    rating = sqlite3.connect(str(server.DB_PATH)).execute(
        "SELECT Rating FROM Feedbacks WHERE UserId = 'user-1' AND BookId = 'b1'"
    ).fetchone()[0]
    assert rating == 5


def test_registrar_feedback_libro_inexistente(server):
    result = server.registrar_feedback("user-1", "no-existe", 4)
    assert result["success"] is False
    assert "no existe" in result["reason"]


def test_registrar_feedback_normaliza_case_del_user_id(server):
    """El feedback se persiste con UserId en minúsculas, sin importar el case enviado."""
    result = server.registrar_feedback("USER-1", "b1", 5, "Excelente")
    assert result["success"] is True
    rows = sqlite3.connect(str(server.DB_PATH)).execute(
        "SELECT UserId FROM Feedbacks WHERE BookId = 'b1'"
    ).fetchall()
    assert rows and all(row[0] == "user-1" for row in rows)


def test_base_datos_no_disponible(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "no-existe.db"))
    from common.settings import clear_settings_cache

    clear_settings_cache()
    import importlib
    import server as server_module

    importlib.reload(server_module)
    server_module.DB_PATH = server_module.get_database_path()

    assert server_module.buscar_libros() == []
    assert server_module.consultar_alquileres_usuario("user-1") == []
    assert server_module.obtener_preferencias("user-1") == []
    assert server_module.listar_recomendaciones_por_genero("user-1") == []
    result = server_module.registrar_feedback("user-1", "b1", 4)
    assert result["success"] is False
