"""Tests unitarios del cliente LLM (app/llm/client.py).

Herméticos: sin red, sin Ollama y sin claves reales. Se parchean las variables
de entorno con ``monkeypatch`` y la construcción de ``langchain_openai.ChatOpenAI``.
"""

from __future__ import annotations

import pytest

import app.llm.client as llm_client


def _patch_chat_openai(monkeypatch) -> dict:
    """Sustituye ChatOpenAI por un fake que captura los kwargs de construcción."""
    captured: dict = {}

    class _FakeChatOpenAI:
        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

    monkeypatch.setattr("langchain_openai.ChatOpenAI", _FakeChatOpenAI)
    return captured


def _clear_llm_env(monkeypatch) -> None:
    for name in (
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "LLM_API_KEY",
        "LLM_MODEL",
        "LLM_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)


def test_ollama_used_when_configured(monkeypatch):
    """(a) OLLAMA_BASE_URL + OLLAMA_MODEL -> ChatOpenAI con base_url, api_key='ollama'."""
    _clear_llm_env(monkeypatch)
    captured = _patch_chat_openai(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "120")

    model = llm_client._langchain_model()

    assert model is not None
    assert captured["kwargs"]["base_url"] == "http://ollama:11434/v1"
    assert captured["kwargs"]["model"] == "llama3.2"
    assert captured["kwargs"]["api_key"] == "ollama"
    assert captured["kwargs"]["timeout"] == 120


def test_ollama_takes_priority_over_cloud(monkeypatch):
    """Ollama tiene prioridad aunque también exista la clave cloud."""
    _clear_llm_env(monkeypatch)
    captured = _patch_chat_openai(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "120")
    monkeypatch.setenv("LLM_API_KEY", "sk-cloud")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")

    llm_client._langchain_model()

    assert captured["kwargs"]["base_url"] == "http://ollama:11434/v1"
    assert captured["kwargs"]["model"] == "llama3.2"
    assert captured["kwargs"]["api_key"] == "ollama"


def test_ollama_without_model_raises(monkeypatch):
    """(b) OLLAMA_BASE_URL definida pero OLLAMA_MODEL ausente -> RuntimeError."""
    _clear_llm_env(monkeypatch)
    _patch_chat_openai(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")

    with pytest.raises(RuntimeError, match="OLLAMA_MODEL"):
        llm_client._langchain_model()


def test_cloud_used_when_ollama_unset(monkeypatch):
    """(c) Sin OLLAMA_BASE_URL + LLM_API_KEY + LLM_MODEL -> ChatOpenAI cloud sin base_url."""
    _clear_llm_env(monkeypatch)
    captured = _patch_chat_openai(monkeypatch)
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "120")

    model = llm_client._langchain_model()

    assert model is not None
    assert "base_url" not in captured["kwargs"]
    assert captured["kwargs"]["model"] == "gpt-4o-mini"
    assert captured["kwargs"]["api_key"] == "sk-test"
    assert captured["kwargs"]["timeout"] == 120


def test_llm_timeout_missing_raises(monkeypatch):
    """LLM habilitado sin LLM_TIMEOUT_SECONDS -> RuntimeError (fail-fast)."""
    _clear_llm_env(monkeypatch)
    _patch_chat_openai(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")

    with pytest.raises(RuntimeError, match="LLM_TIMEOUT_SECONDS"):
        llm_client._langchain_model()


def test_llm_timeout_invalid_raises(monkeypatch):
    """LLM_TIMEOUT_SECONDS no entero positivo -> RuntimeError."""
    _clear_llm_env(monkeypatch)
    _patch_chat_openai(monkeypatch)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "abc")

    with pytest.raises(RuntimeError, match="LLM_TIMEOUT_SECONDS"):
        llm_client._langchain_model()


def test_no_provider_returns_none(monkeypatch):
    """(d) Ningún proveedor configurado -> _langchain_model() devuelve None."""
    _clear_llm_env(monkeypatch)
    _patch_chat_openai(monkeypatch)

    assert llm_client._langchain_model() is None


class _FakeModel:
    def __init__(self, response=None, error=None) -> None:
        self._response = response
        self._error = error
        self.captured_messages = None

    async def ainvoke(self, messages):
        self.captured_messages = messages
        if self._error is not None:
            raise self._error
        return self._response


class _FakeResponse:
    def __init__(self, content) -> None:
        self.content = content


@pytest.mark.asyncio
async def test_generate_recommendation_returns_none_on_error(monkeypatch):
    """(e) ainvoke lanza excepción -> generate_recommendation devuelve None."""
    model = _FakeModel(error=RuntimeError("timeout"))
    monkeypatch.setattr(llm_client, "_langchain_model", lambda: model)

    assert await llm_client.generate_recommendation("contexto de prueba") is None


@pytest.mark.asyncio
async def test_generate_recommendation_returns_none_on_empty_content(monkeypatch):
    """(f) ainvoke devuelve contenido vacío -> None."""
    model = _FakeModel(response=_FakeResponse("   "))
    monkeypatch.setattr(llm_client, "_langchain_model", lambda: model)

    assert await llm_client.generate_recommendation("contexto de prueba") is None


@pytest.mark.asyncio
async def test_generate_recommendation_masks_pii_before_sending(monkeypatch):
    """(g) mask_pii se invoca con el contexto y su salida es la que llega al LLM."""
    model = _FakeModel(response=_FakeResponse("Te recomiendo Cien años de soledad."))
    monkeypatch.setattr(llm_client, "_langchain_model", lambda: model)

    calls = []
    real_mask = llm_client.mask_pii

    def _spy_mask(text: str) -> str:
        calls.append(text)
        return real_mask(text)

    monkeypatch.setattr(llm_client, "mask_pii", _spy_mask)

    result = await llm_client.generate_recommendation("contacta a juan@example.com")

    assert calls == ["contacta a juan@example.com"]
    assert result == "Te recomiendo Cien años de soledad."
    prompt = model.captured_messages[0]["content"]
    assert "[EMAIL]" in prompt
    assert "juan@example.com" not in prompt
