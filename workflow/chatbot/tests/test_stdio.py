"""Tests unitarios del cliente MCP stdio (app/mcp_clients/stdio.py).

No lanzan procesos: solo validan el parseo del comando, la resolución de
variables de entorno y la herencia del entorno hacia los subprocesos MCP.
"""

from __future__ import annotations

import pytest

from app.mcp_clients.stdio import McpStdioClient, _inherit_environment, require_env


def test_command_is_split_into_program_and_args():
    """(a) 'python /app/.../server.py' -> command='python', args=[.../server.py]."""
    client = McpStdioClient(
        "python /app/workflow/mcp/biblioteca-mcp/server.py", "biblioteca"
    )
    assert client._parameters.command == "python"
    assert "/app/workflow/mcp/biblioteca-mcp/server.py" in client._parameters.args


def test_empty_command_raises_value_error():
    """(b) Comando vacío o solo espacios -> ValueError."""
    with pytest.raises(ValueError):
        McpStdioClient("")
    with pytest.raises(ValueError):
        McpStdioClient("   ")


def test_require_env_returns_value_when_set(monkeypatch):
    """(c) Variable definida -> require_env devuelve su valor (recortado)."""
    monkeypatch.setenv("TEST_MCP_VAR", "  valor  ")
    assert require_env("TEST_MCP_VAR") == "valor"


def test_require_env_raises_when_unset(monkeypatch):
    """(c) Variable ausente o vacía -> RuntimeError."""
    monkeypatch.delenv("TEST_MCP_VAR", raising=False)
    with pytest.raises(RuntimeError, match="TEST_MCP_VAR"):
        require_env("TEST_MCP_VAR")
    monkeypatch.setenv("TEST_MCP_VAR", "   ")
    with pytest.raises(RuntimeError, match="TEST_MCP_VAR"):
        require_env("TEST_MCP_VAR")


def test_inherit_environment_includes_project_paths(monkeypatch):
    """(d) DATABASE_PATH y AUDIT_DATABASE_PATH se propagan al entorno MCP."""
    monkeypatch.setenv("DATABASE_PATH", "/app/database/BibliotecaVirtual.db")
    monkeypatch.setenv("AUDIT_DATABASE_PATH", "/app/database/audit.db")

    env = _inherit_environment()

    assert env["DATABASE_PATH"] == "/app/database/BibliotecaVirtual.db"
    assert env["AUDIT_DATABASE_PATH"] == "/app/database/audit.db"
