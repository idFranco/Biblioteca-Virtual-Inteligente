"""Validación de dependencias del chatbot en el arranque y para el healthcheck (US-023).

Funcionalidad:
- ``check_ollama()``  -> fail-fast: verifica que el modelo local Ollama esté activo
  (``OLLAMA_BASE_URL`` alcanzable) y que ``OLLAMA_MODEL`` esté cargado.
- ``check_groq()``    -> fail-fast: verifica conexión a GROQ con ``API_KEY_GROQ``.
- ``probe_health()``  -> sondeo ligero con caché TTL para ``GET /health`` (no lanza);
  devuelve ``{"ollama": ..., "groq": ...}`` con ``ok|down|error``.
- ``python -m app.startup_checks`` -> ejecuta ambos checks y sale 0/1 (fail-fast
  en el CMD del Dockerfile antes de servir con uvicorn).

Reglas:
- No se hardcodean secretos: la clave GROQ solo se lee de ``API_KEY_GROQ`` y nunca
  se imprime; los diagnósticos describen el estado sin exponer la clave.
- Sin variables nuevas: se reutilizan ``OLLAMA_BASE_URL``, ``OLLAMA_MODEL`` y
  ``API_KEY_GROQ``/``GROQ_MODEL``/``GROQ_TIMEOUT_SECONDS`` ya exigidas por compose.
- La caché TTL de ``probe_health()`` evita martillar GROQ en cada sondeo del
  healthcheck (ADR patrón fail-fast, ADR-025).
"""

from __future__ import annotations

import asyncio
import os
import sys
import time

import httpx

GROQ_MODELS_URL = os.getenv(
    "GROQ_MODELS_URL", "https://api.groq.com/openai/v1/models"
)

# Timeouts de la validación de arranque (sin variables nuevas).
_OLLAMA_CHECK_TIMEOUT_SECONDS = 5.0
_GROQ_CHECK_TIMEOUT_SECONDS = float(os.getenv("GROQ_TIMEOUT_SECONDS", "10"))

# Sondeo ligero para /health: timeouts cortos y caché TTL.
_PROBE_TIMEOUT_SECONDS = 3.0
_PROBE_TTL_SECONDS = 30.0

_cache: dict[str, float | dict[str, str]] = {"at": 0.0, "value": None}


def _ollama_base_url() -> str:
    url = os.getenv("OLLAMA_BASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "Falta la variable de entorno 'OLLAMA_BASE_URL' (modelo local Ollama)."
        )
    return url


def _ollama_model() -> str:
    model = os.getenv("OLLAMA_MODEL", "").strip()
    if not model:
        raise RuntimeError(
            "Falta la variable de entorno 'OLLAMA_MODEL', requerida cuando se "
            "define 'OLLAMA_BASE_URL'."
        )
    return model


def _ollama_model_loaded(model: str, available_ids: list[str]) -> bool:
    """True si ``model`` está cargado en Ollama (tolerando el tag por defecto).

    - Si ``model`` incluye tag explícito (``llama3.2:13b``) -> match exacto.
    - Si no (``llama3.2``) -> se considera cargado si existe ``llama3.2`` o
      ``llama3.2:<tag>`` (Ollama reporta ``<name>:<tag>``, tag por defecto
      ``latest``), replicando lo que resuelve el cliente LLM (US-024).
    """
    if ":" in model:
        return model in available_ids
    return model in available_ids or any(
        mid.startswith(f"{model}:") for mid in available_ids
    )


async def check_ollama() -> None:
    """Fail-fast: verifica que el modelo local Ollama esté activo y cargado.

    Lanza ``RuntimeError`` con un diagnóstico claro si el host es inalcanzable,
    la URL responde con error o el modelo configurado no está cargado.
    """
    base = _ollama_base_url()
    model = _ollama_model()
    url = f"{base.rstrip('/')}/models"
    try:
        async with httpx.AsyncClient(timeout=_OLLAMA_CHECK_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"El modelo local Ollama no está activo: no se pudo consultar '{url}' "
            f"({exc.__class__.__name__}: {exc})."
        ) from exc

    ids = [item.get("id") for item in (payload.get("data") or [])]
    if not _ollama_model_loaded(model, ids):
        raise RuntimeError(
            f"El modelo local Ollama no está cargado: '{model}' no aparece en '{url}' "
            f"(modelos disponibles: {', '.join(ids) or 'ninguno'})."
        )


async def check_groq() -> None:
    """Fail-fast: verifica conexión a GROQ con la clave configurada.

    Considera válida una respuesta 200 a ``GET /models``. Lanza ``RuntimeError``
    distinguiendo: clave ausente, clave inválida (401/403) y fallo de red/timeout.
    """
    key = os.getenv("API_KEY_GROQ", "").strip()
    if not key:
        raise RuntimeError(
            "Falta la variable de entorno 'API_KEY_GROQ' (conexión a GROQ)."
        )

    headers = {"Authorization": f"Bearer {key}"}
    try:
        async with httpx.AsyncClient(timeout=_GROQ_CHECK_TIMEOUT_SECONDS) as client:
            response = await client.get(GROQ_MODELS_URL, headers=headers)
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"No hay conexión a GROQ: no se pudo consultar '{GROQ_MODELS_URL}' "
            f"({exc.__class__.__name__})."
        ) from exc

    if response.status_code == 401 or response.status_code == 403:
        raise RuntimeError(
            f"No hay conexión a GROQ: la clave 'API_KEY_GROQ' es inválida o no "
            f"autorizada (HTTP {response.status_code})."
        )
    if response.status_code != 200:
        raise RuntimeError(
            f"No hay conexión a GROQ: la API respondió HTTP {response.status_code} "
            f"al consultar '{GROQ_MODELS_URL}'."
        )


async def run_checks() -> None:
    """Ejecuta los checks de arranque en orden determinista (Ollama, luego GROQ)."""
    await check_ollama()
    await check_groq()


async def _probe_one(check) -> str:
    """Ejecuta un check y devuelve 'ok' / 'down' sin lanzar."""
    try:
        await check()
    except (RuntimeError, httpx.HTTPError):
        return "down"
    return "ok"


async def probe_health() -> dict[str, str]:
    """Sondeo ligero de dependencias para ``GET /health`` (con caché TTL).

    Devuelve ``{"ollama": "ok"|"down", "groq": "ok"|"down"}``. Nunca lanza: un
    proveedor no configurado o con error se reporta como ``down``.
    """
    now = time.monotonic()
    cached_at = _cache["at"]
    cache_value = _cache["value"]
    if isinstance(cache_value, dict) and isinstance(cached_at, float):
        if now - cached_at < _PROBE_TTL_SECONDS:
            return cache_value

    value = {
        "ollama": await _probe_one(check_ollama),
        "groq": await _probe_one(check_groq),
    }
    _cache["at"] = now
    _cache["value"] = value
    return value


async def _main() -> int:
    try:
        await run_checks()
    except RuntimeError as exc:
        print(f"[startup-checks] ERROR: {exc}", file=sys.stderr)
        return 1
    print("[startup-checks] OK: modelo local Ollama activo y conexión a GROQ verificada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))