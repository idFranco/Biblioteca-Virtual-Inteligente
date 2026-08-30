"""Cliente aislado del LLM (LangChain, compatible OpenAI).

Reglas:
- No se hardcodean secretos: la clave de la nube se lee de LLM_API_KEY y el
  proveedor local Ollama usa el placeholder ``"ollama"`` que Ollama ignora.
- Prioridad de proveedores: si ``OLLAMA_BASE_URL`` está definida se usa el
  modelo local Ollama (prioridad sobre la nube); en caso contrario, si
  ``LLM_API_KEY`` está definida se usa el proveedor cloud compatible OpenAI.
- El contexto enviado al proveedor externo debe ir enmascarado (PII masking).
- Si el proveedor no está disponible (sin clave/URL, sin paquete o error de
  red), devuelve None para que el grafo use la respuesta heurística de respaldo
  (ADR-023).
"""

from __future__ import annotations

import os
from typing import Any

from app.prompts import load_recommendation_prompt, load_smalltalk_prompt
from app.utils.pii_masker import mask_pii


def _api_key() -> str | None:
    key = os.getenv("LLM_API_KEY", "").strip()
    return key or None


def _ollama_base_url() -> str | None:
    url = os.getenv("OLLAMA_BASE_URL", "").strip()
    return url or None


def _ollama_model() -> str:
    model = os.getenv("OLLAMA_MODEL", "").strip()
    if not model:
        raise RuntimeError(
            "Falta la variable de entorno 'OLLAMA_MODEL', requerida cuando se define 'OLLAMA_BASE_URL'."
        )
    return model


def _llm_timeout() -> int:
    """Timeout del LLM en segundos (entero positivo, fail-fast)."""
    raw = os.getenv("LLM_TIMEOUT_SECONDS", "").strip()
    try:
        timeout = int(raw)
    except (TypeError, ValueError):
        timeout = 0
    if timeout <= 0:
        raise RuntimeError(
            "Falta la variable de entorno 'LLM_TIMEOUT_SECONDS' o su valor "
            "no es un entero positivo (requerida cuando el LLM está habilitado)."
        )
    return timeout


def _model() -> str:
    model = os.getenv("LLM_MODEL", "").strip()
    if not model:
        raise RuntimeError(
            "Falta la variable de entorno 'LLM_MODEL', requerida cuando se define 'LLM_API_KEY'."
        )
    return model


def _langchain_model() -> Any | None:
    """Construye el chat model de LangChain con el proveedor disponible.

    Prioridad:
    1. Ollama local (``OLLAMA_BASE_URL`` + ``OLLAMA_MODEL``) — prioridad sobre
       la nube; ``api_key="ollama"`` es un placeholder que Ollama ignora.
    2. Nube compatible OpenAI (``LLM_API_KEY`` + ``LLM_MODEL``).
    3. ``None`` (fallback heurístico, ADR-023) si ningún proveedor está
       configurado o el paquete ``langchain_openai`` no está instalado.
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    ollama_url = _ollama_base_url()
    if ollama_url:
        return ChatOpenAI(
            model=_ollama_model(),
            base_url=ollama_url,
            api_key="ollama",  # placeholder que Ollama ignora; no se lee ningún secreto
            temperature=0.4,
            max_tokens=300,
            timeout=_llm_timeout(),
        )

    key = _api_key()
    if not key:
        return None

    return ChatOpenAI(
        model=_model(),
        api_key=key,
        temperature=0.4,
        max_tokens=300,
        timeout=_llm_timeout(),
    )


async def generate_recommendation(context_text: str) -> str | None:
    """Genera una recomendación en lenguaje natural vía el LLM disponible.

    Args:
        context_text: contexto enmascarado (sin PII) con los libros candidatos.

    Returns:
        Texto de la recomendación, o None si el LLM no está disponible o falla
        (el grafo debe usar el fallback heurístico).
    """
    model = _langchain_model()
    if model is None:
        return None

    prompt = load_recommendation_prompt().format(
        context=mask_pii(context_text).strip() or "No hay datos."
    )

    try:
        response = await model.ainvoke([{"role": "user", "content": prompt}])
        text = getattr(response, "content", None)
        if isinstance(text, str) and text.strip():
            return text.strip()
        return None
    except Exception:
        return None


async def generate_smalltalk(user_message: str) -> str | None:
    """Genera una respuesta breve y cortés para conversación casual/smalltalk.

    Usa un prompt dedicado (nunca el de recomendación) para que el LLM no derive
    a recomendar libros inventados en una intención ``other``. Si el LLM no está
    disponible o falla, devuelve None para que el grafo use el fallback de saludo.
    """
    model = _langchain_model()
    if model is None:
        return None

    prompt = load_smalltalk_prompt().format(
        context=mask_pii(user_message).strip() or "No hay datos."
    )

    try:
        response = await model.ainvoke([{"role": "user", "content": prompt}])
        text = getattr(response, "content", None)
        if isinstance(text, str) and text.strip():
            return text.strip()
        return None
    except Exception:
        return None
