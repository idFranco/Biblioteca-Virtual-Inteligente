import json
import sqlite3
import sys
from pathlib import Path

from fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "workflow" / "mcp"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.settings import get_database_path, require_env
import groq_audit
from local_audit import (
    detect_injection_local,
    detect_sensitive_local,
    sanitize_local,
)

mcp = FastMCP("Security-Audit-MCP")

DATABASE_PATH = get_database_path()

_AUDIT_DB_PATH = Path(require_env("AUDIT_DATABASE_PATH")).resolve()
_AUDIT_TABLE = "audit_events"


@mcp.tool()
def ping() -> str:
    return "pong"


def _init_audit_db() -> None:
    """Crea la tabla de auditoría si la base de datos de auditoría existe o puede crearse."""
    if _AUDIT_DB_PATH.parent.is_dir():
        with sqlite3.connect(_AUDIT_DB_PATH) as connection:
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_AUDIT_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    correlation_id TEXT,
                    result TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )


def _register_audit_event(event_type: str, result: str, correlation_id: str | None = None) -> None:
    from datetime import datetime, timezone

    try:
        _init_audit_db()
        with sqlite3.connect(_AUDIT_DB_PATH) as connection:
            connection.execute(
                f"INSERT INTO {_AUDIT_TABLE} (event_type, correlation_id, result, created_at) "
                "VALUES (?, ?, ?, ?)",
                (event_type, correlation_id, result, datetime.now(timezone.utc).isoformat()),
            )
    except Exception:
        return


@mcp.tool()
async def audit_user_input(text: str, correlation_id: str | None = None) -> dict:
    """Audita la entrada del usuario antes de procesarse en el grafo.

    Clasifica inyección y datos sensibles mediante Groq. Si el auditor activo
    (Groq) no está disponible, se degrada al detector local determinista con
    ``degraded=true`` (no es fail-open: niega inyección/PII real por patrones).
    Nunca almacena texto completo ni secretos.
    """
    degraded = False
    try:
        injection = await groq_audit.detect_injection(text)
        sensitive = await groq_audit.detect_sensitive(text)
        safe = not injection and not sensitive
        reasons = injection[:3]
    except Exception:
        injection = detect_injection_local(text)
        sensitive = detect_sensitive_local(text)
        safe = not injection and not sensitive
        reasons = injection[:3]
        degraded = True

    result = json.dumps({"safe": safe, "reasons": reasons, "degraded": degraded})
    _register_audit_event("audit_user_input", result, correlation_id)
    return {
        "safe": safe,
        "reasons": reasons,
        "sensitive": sensitive[:3],
        "degraded": degraded,
    }


@mcp.tool()
async def audit_model_output(text: str, correlation_id: str | None = None) -> dict:
    """Audita la salida del modelo antes de enviarla al frontend.

    Si el auditor activo (Groq) no está disponible, se degrada al detector
    local determinista con ``degraded=true`` (nunca bloquea la salida completa
    por un fallo de infraestructura).
    """
    degraded = False
    try:
        injection = await groq_audit.detect_injection(text)
        sensitive = await groq_audit.detect_sensitive(text)
        safe = not injection and not sensitive
        reasons = (injection + sensitive)[:3]
    except Exception:
        injection = detect_injection_local(text)
        sensitive = detect_sensitive_local(text)
        safe = not injection and not sensitive
        reasons = (injection + sensitive)[:3]
        degraded = True

    result = json.dumps({"safe": safe, "degraded": degraded})
    _register_audit_event("audit_model_output", result, correlation_id)
    return {"safe": safe, "reasons": reasons, "degraded": degraded}


@mcp.tool()
async def detect_prompt_injection(text: str) -> dict:
    """Detecta intentos de prompt injection en el texto vía Groq.

    Se degrada al detector local determinista si Groq no está disponible.
    """
    degraded = False
    try:
        injection = await groq_audit.detect_injection(text)
        flagged = bool(injection)
        reasons = injection[:3]
    except Exception:
        injection = detect_injection_local(text)
        flagged = bool(injection)
        reasons = injection[:3]
        degraded = True

    _register_audit_event("detect_prompt_injection", json.dumps({"flagged": flagged, "degraded": degraded}))
    return {"flagged": flagged, "reasons": reasons, "degraded": degraded}


@mcp.tool()
async def detect_sensitive_data(text: str) -> dict:
    """Detecta datos sensibles (emails, tokens, claves) en el texto vía Groq.

    Se degrada al detector local determinista si Groq no está disponible.
    """
    degraded = False
    try:
        sensitive = await groq_audit.detect_sensitive(text)
        flagged = bool(sensitive)
        patterns = sensitive[:5]
    except Exception:
        sensitive = detect_sensitive_local(text)
        flagged = bool(sensitive)
        patterns = sensitive[:5]
        degraded = True

    _register_audit_event("detect_sensitive_data", json.dumps({"flagged": flagged, "degraded": degraded}))
    return {"flagged": flagged, "patterns": patterns, "degraded": degraded}


@mcp.tool()
async def sanitize_text(text: str) -> dict:
    """Redacta PII y elimina contenido potencialmente peligroso vía Groq.

    Si Groq no está disponible, se degrada al enmascaramiento local por segmentos
    (``sanitize_local``): NUNCA devuelve ``[REDACTED]`` global por un fallo de
    infraestructura; solo enmascara los segmentos detectados.
    """
    degraded = False
    try:
        sanitized, was_sanitized = await groq_audit.sanitize(text)
    except Exception:
        sanitized, was_sanitized = sanitize_local(text)
        degraded = True
    return {
        "safe_text": sanitized,
        "was_sanitized": was_sanitized,
        "degraded": degraded,
    }


@mcp.tool()
def register_audit_event(event_type: str, result: str, correlation_id: str | None = None) -> dict:
    """Registra un evento de auditoría de forma estructurada (sin PII)."""
    _register_audit_event(event_type, result, correlation_id)
    return {"registered": True, "event_type": event_type}


if __name__ == "__main__":
    mcp.run()
