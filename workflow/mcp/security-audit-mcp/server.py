import json
import os
import re
import sqlite3
import sys
from pathlib import Path

from mcp.server import FastMCP

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "workflow" / "mcp"))

from common.settings import get_database_path

mcp = FastMCP("Security-Audit-MCP")

DATABASE_PATH = get_database_path()

_AUDIT_DB_PATH = Path(
    os.getenv("AUDIT_DATABASE_PATH", str(REPO_ROOT / "workflow" / "database" / "AuditLog.db"))
).resolve()
_AUDIT_TABLE = "audit_events"

_INJECTION_PATTERNS = [
    re.compile(r"\bignore (all )?(previous|prior) instructions\b", re.IGNORECASE),
    re.compile(r"\b(system|developer) prompt\b", re.IGNORECASE),
    re.compile(r"\bdisregard\b", re.IGNORECASE),
    re.compile(r"\byou are now\b", re.IGNORECASE),
    re.compile(r"\bdan\s*\.", re.IGNORECASE),
]

_SENSITIVE_PATTERNS = [
    re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(oauth|bearer)\s+[\w.-]+", re.IGNORECASE),
    re.compile(r"\bzsk-[\w-]+\b", re.IGNORECASE),
    re.compile(r"\b(begin )?(private key)\b", re.IGNORECASE),
]


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


def _detect_sensitive(text: str) -> list[str]:
    matches = []
    for pattern in _SENSITIVE_PATTERNS:
        if pattern.search(text) and pattern.pattern not in matches:
            matches.append(pattern.pattern)
    return matches


def _prompt_injection_risk(text: str) -> list[str]:
    matches = []
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text) and pattern.pattern not in matches:
            matches.append(pattern.pattern)
    return matches


@mcp.tool()
def ping() -> str:
    return "pong"


@mcp.tool()
def audit_user_input(text: str, correlation_id: str | None = None) -> dict:
    """Audita la entrada del usuario antes de procesarse en el grafo.

    Devuelve {"safe": bool, "reasons": [...], "sensitive": [...]}. No almacena
    texto completo ni secretos.
    """
    injection = _prompt_injection_risk(text)
    sensitive = _detect_sensitive(text)
    safe = not injection and not sensitive
    result = json.dumps({"safe": safe, "reasons": injection[:3]})
    _register_audit_event("audit_user_input", result, correlation_id)
    return {"safe": safe, "reasons": injection[:3], "sensitive": sensitive[:3]}


@mcp.tool()
def audit_model_output(text: str, correlation_id: str | None = None) -> dict:
    """Audita la salida del modelo antes de enviarla al frontend."""
    injection = _prompt_injection_risk(text)
    sensitive = _detect_sensitive(text)
    safe = not injection and not sensitive
    result = json.dumps({"safe": safe})
    _register_audit_event("audit_model_output", result, correlation_id)
    return {"safe": safe, "reasons": (injection + sensitive)[:3]}


@mcp.tool()
def detect_prompt_injection(text: str) -> dict:
    """Detecta intentos de prompt injection en el texto."""
    injection = _prompt_injection_risk(text)
    _register_audit_event("detect_prompt_injection", json.dumps({"flagged": bool(injection)}))
    return {"flagged": bool(injection), "reasons": injection[:3]}


@mcp.tool()
def detect_sensitive_data(text: str) -> dict:
    """Detecta datos sensibles (emails, tokens, claves) en el texto."""
    sensitive = _detect_sensitive(text)
    _register_audit_event("detect_sensitive_data", json.dumps({"flagged": bool(sensitive)}))
    return {"flagged": bool(sensitive), "patterns": sensitive[:5]}


@mcp.tool()
def sanitize_text(text: str) -> dict:
    """Elimina contenido potencialmente peligroso y redacta PII del texto."""
    sanitized = text
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub("", sanitized)
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    sanitized = re.sub(r"[ \t]{2,}", " ", sanitized).strip()
    return {"safe_text": sanitized, "was_sanitized": sanitized != text}


@mcp.tool()
def register_audit_event(event_type: str, result: str, correlation_id: str | None = None) -> dict:
    """Registra un evento de auditoría de forma estructurada (sin PII)."""
    _register_audit_event(event_type, result, correlation_id)
    return {"registered": True, "event_type": event_type}


if __name__ == "__main__":
    mcp.run()
