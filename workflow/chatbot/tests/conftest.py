import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import pytest

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
def _isolate_mcp_clients(monkeypatch):
    """Aísla los clientes MCP para que los tests no lancen procesos reales.

    Por defecto, el grafo se ejecuta con MCP fuera de servicio (fallback).
    Cada test puede sobrescribir con monkeypatch.
    """
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.mcp_clients.open_library_client as open_library_client
    import app.mcp_clients.security_audit_client as security_client

    async def _no_biblioteca(*args, **kwargs):
        raise RuntimeError("MCP simulado caído")

    async def _no_security(*args, **kwargs):
        raise RuntimeError("MCP simulado caído")

    async def _no_open_library(*args, **kwargs):
        raise RuntimeError("MCP simulado caído")

    monkeypatch.setattr(biblioteca_client, "buscar_libros", _no_biblioteca)
    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", _no_biblioteca)
    monkeypatch.setattr(biblioteca_client, "consultar_alquileres_usuario", _no_biblioteca)
    monkeypatch.setattr(biblioteca_client, "consultar_libro_en_curso", _no_biblioteca)
    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", _no_biblioteca)
    monkeypatch.setattr(biblioteca_client, "listar_recomendaciones_por_genero", _no_biblioteca)
    monkeypatch.setattr(biblioteca_client, "registrar_feedback", _no_biblioteca)
    monkeypatch.setattr(security_client, "audit_input", _no_security)
    monkeypatch.setattr(security_client, "audit_output", _no_security)
    monkeypatch.setattr(security_client, "sanitize_text", _no_security)
    monkeypatch.setattr(open_library_client, "search_books", _no_open_library)
    monkeypatch.setattr(open_library_client, "get_book_details", _no_open_library)
