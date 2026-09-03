"""Auditoría de seguridad local y determinista (fallback).

Se usa cuando la auditoría basada en Groq (``groq_audit.py``) no está
disponible (clave ausente/inválida, cuota, error de red o JSON inválido).

NO es un fail-open: las funciones ``detect_injection_local`` y
``detect_sensitive_local`` son detectores por patrones deterministas que niegan
positivos reales de inyección/PII. El veredicto activo del auditor Groq
continúa siendo fail-closed (bloquear/sanitizar); la degradación solo se actúa
cuando Groq está indisponible y se marca con ``degraded=true`` en el resultado
y en el evento de auditoría.

Reglas:
- ``sanitize_local`` enmascara POR SEGMENTO los datos detectados (nunca
  devuelve ``[REDACTED]`` global por un fallo de infraestructura).
- No se guardan secretos ni texto completo en logs (el enmascaramiento se
  aplica antes de persistir).
"""

from __future__ import annotations

import re

_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "prompt_injection",
        re.compile(
            r"ignor(?:a|e|ad) (?:las |tus |mis )?(?:instrucciones|indicaciones|prompt|reglas)"
            r"|ignore (?:previous|all|prior) instructions"
            r"|system prompt|reveal (?:your )?(?:system|instructions)|est[aá]s desbloqueado",
            re.IGNORECASE,
        ),
    ),
    (
        "credential_request",
        re.compile(
            # 1) VERBO DE PETICIÓN + OBJETO DE CREDENCIAL (ES o EN).
            #    Requiere ambos para evitar falsos positivos: un "token"/"sesión"
            #    mencionado en contexto de libro NO dispara (ADR-040 + US-027).
            r"(?:"
            # Verbos ES
            r"dame|d[aá]me|p[aá]same|pasa|suministr(?:a|ar|e|as)|"
            r"proporcion(?:a|ar|e|as)|facilit(?:a|ar|e|as)|env[ií](?:a|ar|e|as)|"
            r"compart(?:e|ir|a|as)|revel(?:a|ar|e|as)|mu[ée]str(?:a|ar|e|as)|"
            r"necesito|quiero|quisiera|ens[eé][ñn]ame|cu[aá]l es"
            # Verbos EN
            r"|(?:give|send|show|provide|reveal|share|obtain|fetch|access|retrieve)"
            r"(?:\s+(?:me|us|him|her|them))?"
            r"|\bwhat is|\bwhere is|\bi need|\bi want|\btell me|\bgive me\b|\bshow me\b"
            r"|\bmay i have|\bcan i have|\bfetch me\b|\bprovide me with\b"
            r")"
            # Clíticos de objeto + determinantes/posesivos (ES/EN)
            r"\s*(?:me|te|le|nos|los|les|se|du|to|us|them|my|your|his|her|our|their)?"
            r"\s*(?:la|el|los|las|tu|su|mi|mis|de [mt]i|de la|del|de los|de las|"
            r"your|my|our|their|his|her|the|a|an)?"
            r"\s+(?:password|contrase[ñn]a|jwt|token|session|ses(?:si|i)[oó]n|cookie|"
            r"session[ ]?id|authorization|api[ _-]?key|access[ _-]?token|"
            r"secret|secreto|credentials?|credencial(?:es)?|otp|code|pin|"
            r"c[oó]digo|tarjeta)"
            # 2) MENCIÓN BARE de contraseña (ES o EN): dispara sin verbo de petición
            r"|(?:la |el |mi |su |tu |your |my |our |their |the )?"
            r"(?:contrase[ñn]a|password)"
            r"(?:\s+(?:de|del|de la|para|para el|of|for|to)\s+[\w@.-]+)?"
            r"",
            re.IGNORECASE,
        ),
    ),
    (
        "sql_injection_attempt",
        re.compile(
            r"\b(?:drop|truncate|delete|insert|update)\s+(?:table|from|into)\b"
            r"|union\s+select|select[^*]+\s+from|\bselect\s+\*?\s+from\b|;\s*--",
            re.IGNORECASE,
        ),
    ),
    (
        "xss_attempt",
        re.compile(r"<script|</script>|javascript:|onerror\s*=|onload\s*=", re.IGNORECASE),
    ),
    (
        "unauthorized_data_access",
        re.compile(
            r"exfiltra|roba|extrae todos los|accede a (?:la base|datos de otros)"
            r"|data[ _-]?breach",
            re.IGNORECASE,
        ),
    ),
]

_SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "uuid",
        re.compile(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
        ),
    ),
    (
        "email",
        re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ),
    (
        "token",
        re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ),
    (
        "api_key",
        re.compile(r"\b(?:sk|pk|AKIA|ghp|gho)_[A-Za-z0-9_-]{10,}\b"),
    ),
    (
        "credential",
        re.compile(r"\b(?:password|passwd|secret|contrase[ñn]a)\b\s*[:=]\s*\S+", re.IGNORECASE),
    ),
    (
        "card_number",
        re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    ),
    (
        "phone",
        re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}(?!\w)"),
    ),
    (
        "location",
        re.compile(
            r"\b(?:calle|avenida|av\.|ciudad|barrio|colonia|municipio|provincia|vivo en)\s+"
            r"[A-Za-zÁÉÍÓÚáéíóúñÑ0-9\s-]{2,60}",
            re.IGNORECASE,
        ),
    ),
]


def detect_injection_local(text: str) -> list[str]:
    """Detecta intentos de prompt injection por patrones deterministas.

    Returns:
        Lista de categorías de inyección encontradas (vacía si el texto es
        seguro según los patrones locales).
    """
    if not text:
        return []
    return [category for category, pattern in _INJECTION_PATTERNS if pattern.search(text)]


def detect_sensitive_local(text: str) -> list[str]:
    """Detecta datos sensibles o secretos por patrones deterministas.

    Returns:
        Lista de tipos de datos sensibles encontrados (vacía si no hay PII).
    """
    if not text:
        return []
    return [kind for kind, pattern in _SENSITIVE_PATTERNS if pattern.search(text)]


def sanitize_local(text: str) -> tuple[str, bool]:
    """Enmascara por segmento los datos sensibles detectados localmente.

    Reemplaza únicamente los segmentos coincidentes (email, token, tarjeta…)
    conservando el resto del texto. Nunca devuelve ``[REDACTED]`` global.

    Returns:
        Tupla ``(texto_enmascarado, fue_saneado)``.
    """
    if not text:
        return text or "", False
    was_sanitized = False
    masked = text
    for kind, pattern in _SENSITIVE_PATTERNS:
        if pattern.search(masked):
            token = "[ID]" if kind == "uuid" else f"[{kind.upper()}]"
            new_masked = pattern.sub(token, masked)
            if new_masked != masked:
                masked = new_masked
                was_sanitized = True
    return masked, was_sanitized
