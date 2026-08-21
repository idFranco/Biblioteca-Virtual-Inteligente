"""Tests de la configuración CORS del chatbot (workflow/chatbot/main.py).

El app se construye en el import de ``app.main`` llamando a ``_cors_origins()``,
por eso ``CORS_ORIGINS`` se define ANTES de importar el módulo y después se
recarga con ``importlib.reload`` para que el middleware quede registrado con el
origen de prueba. Hermético: el grafo LangGraph se sustituye por un fake.
"""

from __future__ import annotations

import importlib
import os

import pytest
from fastapi.testclient import TestClient

# Debe definirse antes del import de main (fail-fast de _cors_origins).
os.environ["CORS_ORIGINS"] = "http://a.com, http://b.com"

import main as main_module  # noqa: E402

main_module = importlib.reload(main_module)  # re-construye el app con CORS


class _FakeGraph:
    """Fake del grafo LangGraph: ainvoke devuelve un estado sin red."""

    async def ainvoke(self, state):
        return {
            "message": state.message,
            "response": "Respuesta de prueba",
            "recommendations": [],
            "action_offer": None,
        }


def _patch_graph(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "graph", _FakeGraph())


def test_cors_origins_splits_and_strips():
    """(a) 'http://a.com, http://b.com' -> lista con ambos orígenes recortados."""
    assert main_module._cors_origins() == ["http://a.com", "http://b.com"]


def test_cors_origins_missing_raises(monkeypatch):
    """(b) CORS_ORIGINS ausente -> RuntimeError (fail-fast, ADR-025)."""
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        main_module._cors_origins()


def test_preflight_allowed_origin():
    """(c) Preflight OPTIONS con origen permitido -> 200 + Access-Control-Allow-Origin."""
    client = TestClient(main_module.app)
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://a.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://a.com"


def test_post_chat_allowed_origin(monkeypatch):
    """(d) POST /chat con origen permitido -> 200 + Access-Control-Allow-Origin."""
    _patch_graph(monkeypatch)
    client = TestClient(main_module.app)
    response = client.post(
        "/chat",
        json={"message": "hola", "userId": "user-1"},
        headers={"Origin": "http://a.com", "X-Correlation-ID": "corr-test"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://a.com"
    assert response.json()["message"] == "Respuesta de prueba"


def test_post_chat_disallowed_origin_has_no_acao(monkeypatch):
    """(e) Origen no permitido -> respuesta sin cabecera Access-Control-Allow-Origin."""
    _patch_graph(monkeypatch)
    client = TestClient(main_module.app)
    response = client.post(
        "/chat",
        json={"message": "hola"},
        headers={"Origin": "http://evil.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_preflight_disallowed_origin_has_no_acao():
    """Preflight con origen no permitido -> sin cabecera ACAO."""
    client = TestClient(main_module.app)
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers
