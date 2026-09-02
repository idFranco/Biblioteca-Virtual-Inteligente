"""Tests de la validación de arranque y sondeo /health (app/startup_checks.py, US-023).

Herméticos: sin red, sin Ollama y sin claves reales. Se parchea
``httpx.AsyncClient`` con un fake que devuelve respuestas por URL, y se controlan
las variables de entorno con ``monkeypatch``.
"""

from __future__ import annotations

import httpx
import pytest

import app.startup_checks as checks


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}", request=None, response=self
            )

    def json(self) -> dict:
        return self._payload or {}


class _FakeAsyncClient:
    """Cliente httpx fake: responde según la URL pedida (dict url -> handler)."""

    def __init__(self, handler, **kwargs) -> None:
        self._handler = handler
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc) -> None:
        return None

    async def get(self, url, **kwargs):
        return self._handler(url)


def _install_client(monkeypatch, handler) -> None:
    """Sustituye httpx.AsyncClient para que capture el timeout y delegue en handler."""

    def _factory(timeout=None, **kwargs) -> _FakeAsyncClient:
        kwargs["timeout"] = timeout
        return _FakeAsyncClient(handler, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", _factory)


def _clear_env(monkeypatch) -> None:
    for name in ("OLLAMA_BASE_URL", "OLLAMA_MODEL", "API_KEY_GROQ"):
        monkeypatch.delenv(name, raising=False)


def _ollama_models_payload(models: list[str]) -> dict:
    return {"data": [{"id": model} for model in models]}


# ── check_ollama ────────────────────────────────────────────────

def test_ollama_ok_happy_path(monkeypatch):
    """(a) OLLAMA_BASE_URL + OLLAMA_MODEL cargado -> no lanza."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    _install_client(
        monkeypatch, lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.2"]))
    )

    asyncio_run(checks.check_ollama())


def test_ollama_missing_base_url_raises(monkeypatch):
    """(b) OLLAMA_BASE_URL ausente -> RuntimeError (fail-fast)."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")

    with pytest.raises(RuntimeError, match="OLLAMA_BASE_URL"):
        asyncio_run(checks.check_ollama())


def test_ollama_missing_model_raises(monkeypatch):
    """(c) OLLAMA_MODEL ausente -> RuntimeError."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")

    with pytest.raises(RuntimeError, match="OLLAMA_MODEL"):
        asyncio_run(checks.check_ollama())


def test_ollama_unreachable_raises(monkeypatch):
    """(d) Host inalcanzable (ConnectError) -> RuntimeError con diagnóstico."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.255.255.1:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")

    def _boom(url):
        raise httpx.ConnectError("connection refused")

    _install_client(monkeypatch, _boom)

    with pytest.raises(RuntimeError, match="no está activo"):
        asyncio_run(checks.check_ollama())


def test_ollama_http_error_raises(monkeypatch):
    """(e) La URL responde 500 -> RuntimeError."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    _install_client(monkeypatch, lambda url: _FakeResponse(500))

    with pytest.raises(RuntimeError, match="no está activo"):
        asyncio_run(checks.check_ollama())


def test_ollama_model_unloaded_raises(monkeypatch):
    """(f) El modelo no está en la lista -> RuntimeError mencionando el modelo."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    _install_client(
        monkeypatch, lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.1"]))
    )

    with pytest.raises(RuntimeError, match="llama3.2"):
        asyncio_run(checks.check_ollama())


# ── check_ollama: tolerancia al tag de Ollama (US-024) ──────────

def test_ollama_ok_when_model_has_tag_suffix(monkeypatch):
    """(g) OLLAMA_MODEL sin tag y modelo cargado con tag :latest -> no lanza."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    _install_client(
        monkeypatch,
        lambda url: _FakeResponse(
            200, _ollama_models_payload(["qwen3:8b", "llama3.2:latest"])
        ),
    )

    asyncio_run(checks.check_ollama())


def test_ollama_ok_when_model_match_without_tag(monkeypatch):
    """(h) OLLAMA_MODEL sin tag y modelo cargado sin tag -> no lanza (regresión)."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    _install_client(monkeypatch, lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.2"])))

    asyncio_run(checks.check_ollama())


def test_ollama_ok_when_explicit_tag_matches(monkeypatch):
    """(i) OLLAMA_MODEL con tag explícito y ese tag cargado -> no lanza."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:13b")
    _install_client(
        monkeypatch,
        lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.2:latest", "llama3.2:13b"])),
    )

    asyncio_run(checks.check_ollama())


def test_ollama_explicit_tag_does_not_match_other_tag(monkeypatch):
    """(j) Tag explícito no matchea otro tag del mismo modelo -> RuntimeError."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:13b")
    _install_client(monkeypatch, lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.2:latest"])))

    with pytest.raises(RuntimeError, match="llama3.2:13b"):
        asyncio_run(checks.check_ollama())


def test_ollama_without_tag_does_not_match_other_model(monkeypatch):
    """(k) Sin tag no matchea un modelo distinto (sin falso positivo)."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.1")
    _install_client(
        monkeypatch,
        lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.2:latest"])),
    )

    with pytest.raises(RuntimeError, match="llama3.1"):
        asyncio_run(checks.check_ollama())


# ── check_groq ──────────────────────────────────────────────────

def test_groq_ok_happy_path(monkeypatch):
    """(g) API_KEY_GROQ configurada y 200 -> no lanza."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")
    _install_client(monkeypatch, lambda url: _FakeResponse(200, {"data": []}))

    asyncio_run(checks.check_groq())


def test_groq_missing_key_raises(monkeypatch):
    """(h) API_KEY_GROQ ausente -> RuntimeError."""
    _clear_env(monkeypatch)
    with pytest.raises(RuntimeError, match="API_KEY_GROQ"):
        asyncio_run(checks.check_groq())


def test_groq_invalid_key_raises_401(monkeypatch):
    """(i) 401 -> RuntimeError de clave inválida."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_KEY_GROQ", "sk-invalid")
    _install_client(monkeypatch, lambda url: _FakeResponse(401))

    with pytest.raises(RuntimeError, match="inválida"):
        asyncio_run(checks.check_groq())


def test_groq_invalid_key_raises_403(monkeypatch):
    """(j) 403 -> RuntimeError de clave inválida."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_KEY_GROQ", "sk-invalid")
    _install_client(monkeypatch, lambda url: _FakeResponse(403))

    with pytest.raises(RuntimeError, match="inválida"):
        asyncio_run(checks.check_groq())


def test_groq_network_error_raises(monkeypatch):
    """(k) Fallo de red -> RuntimeError de sin conexión."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _boom(url):
        raise httpx.ConnectError("connection refused")

    _install_client(monkeypatch, _boom)

    with pytest.raises(RuntimeError, match="No hay conexión a GROQ"):
        asyncio_run(checks.check_groq())


# ── probe_health (sondeo ligero /health) ────────────────────────

def test_probe_health_reports_ok_when_both_up(monkeypatch):
    """(l) Ollama + GROQ OK -> {'ollama': 'ok', 'groq': 'ok'}."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _handler(url):
        if "ollama" in url:
            return _FakeResponse(200, _ollama_models_payload(["llama3.2"]))
        return _FakeResponse(200, {"data": []})

    _install_client(monkeypatch, _handler)

    result = asyncio_run(checks.probe_health())
    assert result == {"ollama": "ok", "groq": "ok"}


def test_probe_health_reports_down_when_ollama_down(monkeypatch):
    """(m) Ollama caído -> 'ollama': 'down'; 'groq' sigue ok. Sin excepciones."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.255.255.1:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _handler(url):
        if "ollama" in url:
            raise httpx.ConnectError("connection refused")
        return _FakeResponse(200, {"data": []})

    _install_client(monkeypatch, _handler)

    result = asyncio_run(checks.probe_health())
    assert result == {"ollama": "down", "groq": "ok"}


def test_probe_health_reports_down_when_key_missing(monkeypatch):
    """(n) Sin API_KEY_GROQ -> 'groq': 'down' sin lanzar."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    _install_client(
        monkeypatch, lambda url: _FakeResponse(200, _ollama_models_payload(["llama3.2"]))
    )

    result = asyncio_run(checks.probe_health())
    assert result == {"ollama": "ok", "groq": "down"}


def test_probe_health_ollama_ok_with_tag_suffix(monkeypatch):
    """(n') /health reporta ollama ok cuando el modelo tiene tag :latest."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _handler(url):
        if "ollama" in url:
            return _FakeResponse(200, _ollama_models_payload(["llama3.2:latest"]))
        return _FakeResponse(200, {"data": []})

    _install_client(monkeypatch, _handler)

    result = asyncio_run(checks.probe_health())
    assert result == {"ollama": "ok", "groq": "ok"}


def test_probe_health_uses_cache_within_ttl(monkeypatch):
    """(o) Dentro del TTL no se vuelve a consultar la red (DRY: una sola llamada)."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    calls = []

    def _handler(url):
        calls.append(url)
        if "ollama" in url:
            return _FakeResponse(200, _ollama_models_payload(["llama3.2"]))
        return _FakeResponse(200, {"data": []})

    _install_client(monkeypatch, _handler)

    asyncio_run(checks.probe_health())
    asyncio_run(checks.probe_health())
    asyncio_run(checks.probe_health())

    # 1 llamada a ollama + 1 a groq en total (el resto vino de la caché).
    assert len([c for c in calls if "ollama" in c]) == 1
    assert len([c for c in calls if "groq" in c]) == 1


# ── run_checks / __main__ ───────────────────────────────────────

def test_run_checks_passes_when_both_ok(monkeypatch):
    """(p) Ambos OK -> run_checks no lanza."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _handler(url):
        if "ollama" in url:
            return _FakeResponse(200, _ollama_models_payload(["llama3.2"]))
        return _FakeResponse(200, {"data": []})

    _install_client(monkeypatch, _handler)

    asyncio_run(checks.run_checks())


def test_main_exit_zero_when_ok(monkeypatch):
    """(q) _main() -> 0 cuando ambos checks pasan."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _handler(url):
        if "ollama" in url:
            return _FakeResponse(200, _ollama_models_payload(["llama3.2"]))
        return _FakeResponse(200, {"data": []})

    _install_client(monkeypatch, _handler)

    assert asyncio_run(checks._main()) == 0


def test_main_exit_one_on_failure(monkeypatch):
    """(r) _main() -> 1 cuando un check falla."""
    _clear_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://10.255.255.1:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("API_KEY_GROQ", "sk-test")

    def _handler(url):
        raise httpx.ConnectError("connection refused")

    _install_client(monkeypatch, _handler)

    assert asyncio_run(checks._main()) == 1


def asyncio_run(coro):
    """Ejecuta una corutina síncronamente (pytest-asyncio auto no aplica en test de main)."""
    import asyncio

    return asyncio.run(coro)


# Cleanup del estado de la caché entre tests.
@pytest.fixture(autouse=True)
def _reset_cache():
    checks._cache["at"] = 0.0
    checks._cache["value"] = None
    yield
    checks._cache["at"] = 0.0
    checks._cache["value"] = None