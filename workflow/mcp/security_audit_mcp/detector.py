"""Detección pura (sin FastMCP) de prompt injection y datos sensibles.

Separa la lógica de auditoría del servidor MCP para poder probarla de forma
aislada (tests pytest) sin arrancar el transporte. Cubre patrones en español e
inglés y no almacena texto completo ni secretos.
"""

from __future__ import annotations

import re

_INJECTION_PATTERNS = [
    re.compile(r"\bignore (all )?(previous|prior) instructions\b", re.IGNORECASE),
    re.compile(r"\b(system|developer) prompt\b", re.IGNORECASE),
    re.compile(r"\bdisregard\b", re.IGNORECASE),
    re.compile(r"\byou are now\b", re.IGNORECASE),
    re.compile(r"\bdan\s*\.", re.IGNORECASE),
    re.compile(r"\bignora (todas )?(las |tus )?(instrucciones|indicaciones|reglas)( anteriores| previas)?\b", re.IGNORECASE),
    re.compile(r"\bolvida (todas )?(las |tus )?(instrucciones|indicaciones|reglas)\b", re.IGNORECASE),
    re.compile(r"\bno sigas (las |tus )?(instrucciones|indicaciones|reglas)\b", re.IGNORECASE),
    re.compile(r"\bpasa por alto (las |tus )?(instrucciones|indicaciones|reglas)\b", re.IGNORECASE),
    re.compile(r"\bhaz caso omiso\b", re.IGNORECASE),
    re.compile(r"\bprompt del sistema\b", re.IGNORECASE),
    re.compile(r"\bte libero de (tus )?restricciones\b", re.IGNORECASE),
    re.compile(r"\b(ignora|olvida) lo anterior\b", re.IGNORECASE),
    re.compile(
        r"\b(revela|muestra|dime|devuelve|accede a) .*"
        r"(contraseña|password|clave|secreto|token|jwt|credentials)\b",
        re.IGNORECASE,
    ),
]

_SENSITIVE_PATTERNS = [
    re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(oauth|bearer)\s+[\w.-]+", re.IGNORECASE),
    re.compile(r"\bzsk-[\w-]+\b", re.IGNORECASE),
    re.compile(r"\b(begin )?(private key)\b", re.IGNORECASE),
]


def detect_injection(text: str) -> list[str]:
    """Detecta intentos de prompt injection. Devuelve los patrones coincidentes."""
    matches: list[str] = []
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text) and pattern.pattern not in matches:
            matches.append(pattern.pattern)
    return matches


def detect_sensitive(text: str) -> list[str]:
    """Detecta datos sensibles (emails, tokens, claves). Devuelve los patrones."""
    matches: list[str] = []
    for pattern in _SENSITIVE_PATTERNS:
        if pattern.search(text) and pattern.pattern not in matches:
            matches.append(pattern.pattern)
    return matches


def sanitize(text: str) -> tuple[str, bool]:
    """Elimina coincidencias de inyección y redacta PII.

    Returns:
        Tupla ``(texto_saneado, fue_saneado)``.
    """
    sanitized = text
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub("", sanitized)
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    sanitized = re.sub(r"[ \t]{2,}", " ", sanitized).strip()
    return sanitized, sanitized != text
