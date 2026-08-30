"""Verificación de limpieza E2E (US-020, item 4 / criterio #4).

Comprueba que las bases runtime quedaron sin residuo de pruebas E2E y con los
datos demo intactos. Se ejecuta después de aplicar cleanup_biblioteca.sql y
cleanup_audit.sql sobre las bases runtime.

Uso:
    python3 workflow/database/verify_cleanup.py
"""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "workflow" / "database" / "BibliotecaVirtual.db"
AUDIT_PATH = ROOT / "workflow" / "database" / "audit.db"

E2E_USER_ID = "93C1CA75-58A0-4EAA-BA95-CFB887860A50"

EXPECTED_BOOK_COUNT = 50


def check(condition: bool, label: str) -> None:
    status = "OK " if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        raise SystemExit(f"Verificación fallida: {label}")


def col(conn: sqlite3.Connection, query: str, params=()) -> int:
    return int(conn.execute(query, params).fetchone()[0])


def main() -> None:
    biblio = os.environ.get("BIBLIOTECA_DB_PATH") or str(DB_PATH)
    audit = os.environ.get("AUDIT_DB_PATH") or str(AUDIT_PATH)
    bdb = sqlite3.connect(biblio)
    adb = sqlite3.connect(audit)

    check(col(bdb, "SELECT COUNT(*) FROM AspNetUsers") == 1,
          "Solo queda el administrador en AspNetUsers")
    check(col(bdb, "SELECT COUNT(*) FROM AspNetUsers WHERE Email = 'admin@biblioteca.local'") == 1,
          "El admin se conserva")
    check(col(bdb, "SELECT COUNT(*) FROM AspNetUsers WHERE Email = 'usuario.e2e@test.local'") == 0,
          "El usuario E2E fue eliminado")
    check(col(bdb, "SELECT COUNT(*) FROM Books") == EXPECTED_BOOK_COUNT,
          f"Books == {EXPECTED_BOOK_COUNT}")
    check(col(bdb, "SELECT COUNT(*) FROM Rentals WHERE UserId = ?", (E2E_USER_ID,)) == 0,
          "Sin alquileres del usuario E2E")
    check(col(bdb, "SELECT COUNT(*) FROM Notifications WHERE UserId = ?", (E2E_USER_ID,)) == 0,
          "Sin notificaciones del usuario E2E")
    check(col(bdb, "SELECT COUNT(*) FROM BookRequests WHERE RequestedBy = ?", (E2E_USER_ID,)) == 0,
          "Sin book-requests del usuario E2E")
    check(col(bdb, "SELECT COUNT(*) FROM RefreshTokens WHERE UserId = ?", (E2E_USER_ID,)) == 0,
          "Sin refresh tokens del usuario E2E")

    fk = bdb.execute("PRAGMA foreign_key_check").fetchall()
    check(len(fk) == 0, f"PRAGMA foreign_key_check sin violaciones ({len(fk)})")

    audit_rows = col(adb, "SELECT COUNT(*) FROM audit_events "
                          "WHERE correlation_id LIKE 'e2e-%' OR correlation_id LIKE 'test-%'")
    check(audit_rows == 0, f"audit.db sin filas e2e-*/test-* (restantes: {audit_rows})")

    print("\nLimpieza verificada correctamente.")


if __name__ == "__main__":
    main()
