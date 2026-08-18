"""Cliente aislado del LLM externo (LangChain, compatible OpenAI).

Reglas:
- No se hardcodean secretos: la clave se lee de la variable LLM_API_KEY.
- El contexto enviado al proveedor externo debe ir enmascarado (PII masking).
- Si el proveedor no está disponible (sin clave, sin paquete o error de red),
  devuelve None para que el grafo use la respuesta heurística de respaldo.
"""

from __future__ import annotations

import os
from typing import Any

from app.prompts import load_recommendation_prompt
from app.utils.pii_masker import mask_pii

DEFAULT_MODEL = "gpt-4o-mini"


def _api_key() -> str | None:
    key = os.getenv("LLM_API_KEY", "").strip()
    return key or None


def _model() -> str:
    return os.getenv("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _langchain_model() -> Any | None:
    """Construye el chat model de LangChain si el paquete y la clave existen."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    key = _api_key()
    if not key:
        return None

    return ChatOpenAI(
        model=_model(),
        api_key=key,
        temperature=0.4,
        max_tokens=300,
        timeout=20,
    )


async def generate_recommendation(context_text: str) -> str | None:
    """Genera una recomendación en lenguaje natural vía el LLM externo.

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
