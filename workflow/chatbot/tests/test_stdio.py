"""Tests unitarios del cliente MCP stdio (app/mcp_clients/stdio.py).

No lanzan procesos: solo validan el parseo del comando, la resolución de
variables de entorno, la herencia del entorno y la extracción de resultados
tipo ``CallToolResult``.
"""

from __future__ import annotations

import pytest

from app.mcp_clients.stdio import McpStdioClient, _inherit_environment, _parse_result, require_env


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


class _FakeContent:
    def __init__(self, text: str):
        self.text = text


class _FakeCallToolResult:
    """Doble mínimo de la clase CallToolResult del SDK de MCP.

    Expone ``is_error``, ``content`` y ``structured_content`` para simular los
dos caminos de parseo de ``_parse_result`` sin lanzar procesos.
    """

    def __init__(self, *, is_error=False, content=None, structured_content=None):
        self.isError = is_error
        self.is_error = is_error
        self.content = content or []
        self.structured_content = structured_content


def test_parse_result_prefers_structured_content():
    """(e) structured_content (dict ya parseado) se devuelve tal cual."""
    result = _FakeCallToolResult(
        content=[_FakeContent('{"safe_text": "x"}')],
        structured_content={"safe_text": "x"},
    )
    assert _parse_result(result) == {"safe_text": "x"}


def test_parse_result_parses_json_from_text_content():
    """(f) Sin structured_content, parsea el JSON del TextContent."""
    result = _FakeCallToolResult(content=[_FakeContent('{"estado": "en_curso"}')])
    assert _parse_result(result) == {"estado": "en_curso"}


def test_parse_result_returns_plain_text_when_not_json():
    """(g) Texto que no es JSON se devuelve como str puro."""
    result = _FakeCallToolResult(content=[_FakeContent("hola")])
    assert _parse_result(result) == "hola"


def test_parse_result_raises_on_error_result():
    """(h) Un resultado MCP con isError=True lanza RuntimeError."""
    result = _FakeCallToolResult(is_error=True, content=[_FakeContent("boom")])
    with pytest.raises(RuntimeError, match="MCP tool returned error"):
        _parse_result(result)


def test_parse_result_never_returns_raw_object():
    """(i) Un resultado inesperado no se devuelve como objeto crudo.

    Si el resultado no expone el API esperado, se propaga la excepción en lugar
de devolver el objeto MCP (evita fugas de repr en la respuesta).
    """
    class _Weird:
        pass

    with pytest.raises(AttributeError):
        _parse_result(_Weird())
