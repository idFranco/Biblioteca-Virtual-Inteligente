"""Acceso a SQLite en modo lectura con WAL para los servidores MCP.

Los servidores MCP solo leen la base de datos. Los errores de base de datos se
marcan de forma explícita (nunca se exponen detalles internos a los usuarios).
"""

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Sequence


class DbAccess:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.available = database_path.is_file()

    def query(self, sql: str, params: Sequence[object] = ()) -> list[tuple[Any, ...]]:
        """Ejecuta una consulta de solo lectura y devuelve las filas."""
        if not self.available:
            raise RuntimeError("La base de datos no está disponible.")

        with closing(sqlite3.connect(f"file:{self.database_path}?mode=ro", uri=True)) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.execute(sql, params)) as cursor:
                return [tuple(row) for row in cursor.fetchall()]

    def execute(self, sql: str, params: Sequence[object] = ()) -> int:
        """Ejecuta una sentencia de escritura y devuelve el número de filas afectadas.

        Solo se usa por Security-Audit-MCP para registrar eventos de auditoría.
        """
        if not self.available:
            raise RuntimeError("La base de datos no está disponible.")

        with closing(sqlite3.connect(self.database_path)) as connection:
            with closing(connection.execute(sql, params)) as cursor:
                connection.commit()
                return cursor.rowcount
