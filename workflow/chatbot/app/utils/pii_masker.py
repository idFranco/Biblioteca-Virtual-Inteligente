"""Utilidad de enmascaramiento de PII antes de enviar contexto al LLM externo.

Regla chatbot-rules: nunca enviar emails, nombres reales o ubicaciones exactas
al proveedor LLM externo. Este módulo enmascara esos patrones de forma
determinista para que no salgan del chatbot.
"""

from __future__ import annotations

import re

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?!\w)")
_LOCATION = re.compile(
    r"\b(?:calle|avenida|av\.|ciudad|barrio|colonia|municipio|provincia)\s+[A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s-]{2,60}",
    re.IGNORECASE,
)


def mask_pii(text: str) -> str:
    """Reemplaza patrones de PII por tokens genéricos.

    Args:
        text: texto a enmascarar.

    Returns:
        Texto con emails, teléfonos, UUIDs, JWT y ubicaciones enmascarados.
    """
    if not text:
        return text

    masked = _EMAIL.sub("[EMAIL]", text)
    masked = _UUID.sub("[ID]", masked)
    masked = _JWT.sub("[TOKEN]", masked)
    masked = _PHONE.sub("[TEL]", masked)
    masked = _LOCATION.sub("[UBICACIÓN]", masked)
    return masked


def mask_message(message: str, user_id: str | None) -> str:
    """Enmascara un mensaje de usuario para enviarlo al LLM.

    El user_id (identificador interno) también se sustituye para no exponerlo.
    """
    masked = mask_pii(message)
    if user_id:
        masked = masked.replace(user_id, "[USUARIO]")
    return masked
