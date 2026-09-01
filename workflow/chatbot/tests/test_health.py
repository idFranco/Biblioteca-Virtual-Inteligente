"""Tests de GET /health con dependencias reales (app/startup_checks, US-023).

Se parchea ``probe_health`` de main para devolver escenarios deterministicos sin
red. El app se construye al importar ``app.main`` (CORS fail-fast), por eso se
define ``CORS_ORIGINS`` antes del import.
"""

from __future__ import annotations

import importlib
import os

from fastapi.testclient import TestClient

# Mismo valor que test_cors.py: el import de main dispara _cors_origins().
os.environ["CORS_ORIGINS"] = "http://a.com, http://b.com"

import main as main_module  # noqa: E402

main_module = importlib.reload(main_module)


async def _healthy_probe():
    return {"ollama": "ok", "groq": "ok"}


async def _ollama_down_probe():
    return {"ollama": "down", "groq": "ok"}


async def _groq_down_probe():
    return {"ollama": "ok", "groq": "down"}


async def _both_down_probe():
    return {"ollama": "down", "groq": "down"}


def _patch_probe(monkeypatch, probe) -> None:
    monkeypatch.setattr(main_module, "probe_health", probe)


def test_health_healthy_when_dependencies_ok(monkeypatch):
    """(a) Ollama + GROQ OK -> 200 con status healthy y campos ok."""
    _patch_probe(monkeypatch, _healthy_probe)
    client = TestClient(main_module.app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["ollama"] == "ok"
    assert body["groq"] == "ok"


def test_health_degraded_when_ollama_down(monkeypatch):
    """(b) Ollama down -> 503 degraded con ollama=down."""
    _patch_probe(monkeypatch, _ollama_down_probe)
    client = TestClient(main_module.app)
    response = client.get("/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["ollama"] == "down"
    assert body["groq"] == "ok"


def test_health_degraded_when_groq_down(monkeypatch):
    """(c) GROQ down -> 503 degraded con groq=down."""
    _patch_probe(monkeypatch, _groq_down_probe)
    client = TestClient(main_module.app)
    response = client.get("/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["groq"] == "down"


def test_health_degraded_when_both_down(monkeypatch):
    """(d) Ambas down -> 503 degraded."""
    _patch_probe(monkeypatch, _both_down_probe)
    client = TestClient(main_module.app)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"