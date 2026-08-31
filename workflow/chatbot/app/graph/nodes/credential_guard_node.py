"""Nodo determinista de rechazo de credenciales (defensa en profundidad, US-021).

Se ejecuta después de ``audit_input_node`` y antes de cualquier razonamiento
LLM. Si el mensaje pide credenciales (JWT, token, contraseña, API key…),
responde con un rechazo de seguridad fijo y cortés sin exponer ni discutir
credenciales, y sin caer en el fallback de catálogo.

Diseño (ADR-040):
- La detección exige un VERBO de petición combinado con un OBJETO de
  credencial, usando normalización de acentos y tokenización. Esto evita
  falsos positivos de mensajes legítimos que solo mencionan «token» en
  contexto de libro (sin verbo de petición no dispara).
- Los sustantivos de credencial inequívocos (``contraseña``/``password``)
  disparan incluso sin verbo (AC 1b: «la contraseña del admin»).
- Implementación basada en tokenización: se usa ``\b`` + clases de caracteres
  acentuadas dentro de ``(?:...)`` produce un falso negativo en el módulo ``re``
  de Python (p. ej. ``sesión``/``contraseña`` no se detectaban). La
  normalización de acentos + tableros de tokens elimina esa fragilidad.

La respuesta del guard pasa SIEMPRE por ``audit_output_node`` (auditoría de
salida obligatoria, ADR-008/034).
"""

from __future__ import annotations

import re
import unicodedata

from app.graph.state import ChatState

GUARD_RESPONSE = (
    "Lo siento, no puedo facilitar credenciales, tokens ni datos de acceso. "
    "Si necesitas ayuda con tu cuenta, contacta con el administrador de la "
    "biblioteca. ¿Quieres que te recomiende algún libro mientras tanto?"
)


def _normalize(message: str) -> str:
    """Reduce a minúsculas y sin diacríticos para comparación de tokens.

    Usa descomposición Unicode NFKD y elimina las marcas combinables, de modo
    que palabras acentuadas («sesión», «contraseña») se convierten a su forma
    ASCII («sesion», «contrasena») sin depender de los límites de palabra del
    módulo ``re`` (que producen falsos negativos con clases acentuadas).
    """
    text = message.lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


# Verbos de petición (ES + EN) — tokens de una sola palabra (sin acentos).
_REQUEST_VERB_TOKENS = {
    "dame", "deme", "dar", "darte", "darle", "darles", "darnos",
    "pasame", "pasa", "pasar",
    "suministra", "suministrar", "suministre", "suministras",
    "proporciona", "proporcionar", "proporcione", "proporcionas",
    "muestra", "muestre", "muestras", "mostrar", "muestrame", "muestrate",
    "revela", "revelar", "revele", "revelas",
    "envia", "enviar", "envie", "envies",
    "facilita", "facilitar", "facilite", "facilitas",
    "comparte", "compartir", "comparta", "compartas",
    "give", "send", "provide", "show", "reveal", "share",
}

# Frases verbales de petición de varias palabras (EN).
_REQUEST_VERB_PHRASES = ("give me", "send me", "show me")

# Objetos de credencial — tokens de una sola palabra (sin acentos).
_CREDENTIAL_OBJECT_TOKENS = {
    "jwt", "token", "tokens", "password", "contrasena",
    "credencial", "credenciales", "apikey", "api_key",
    "secret", "secreto", "secretos",
    "sesion", "session", "cookie", "cookies",
}

# Frases de objeto de credencial de varias palabras.
_CREDENTIAL_OBJECT_PHRASES = ("api key", "api keys", "access token")

# Sustantivos de credencial inequívocos: disparan incluso sin verbo.
_BARE_CREDENTIAL_TOKENS = {"contrasena", "password"}

# Clíticos de objeto/reflexivos que pueden añadirse a un verbo imperativo
# («envíame», «muéstrame», «pásame») para detectar la forma conjugada.
_CLITICS = ("me", "te", "se", "le", "nos", "les")

_WORD_RE = re.compile(r"[a-z0-9_]+")


def _is_request_verb(token: str) -> bool:
    """True si el token es un verbo de petición (o su forma con clítico)."""
    if token in _REQUEST_VERB_TOKENS:
        return True
    for clitic in _CLITICS:
        if token.endswith(clitic) and token[: -len(clitic)] in _REQUEST_VERB_TOKENS:
            return True
    return False


def _requests_credentials(message: str) -> bool:
    """Determina si el mensaje pide credenciales (heurística determinista).

    Se activa si el mensaje contiene un verbo de petición Y un objeto de
    credencial, o una mención inequívoca de contraseña/password.
    """
    if not message:
        return False
    text = _normalize(message)
    tokens = set(_WORD_RE.findall(text))

    has_request_verb = any(_is_request_verb(t) for t in tokens) or any(
        phrase in text for phrase in _REQUEST_VERB_PHRASES
    )
    has_credential_object = bool(tokens & _CREDENTIAL_OBJECT_TOKENS) or any(
        phrase in text for phrase in _CREDENTIAL_OBJECT_PHRASES
    )
    bare_credential = bool(tokens & _BARE_CREDENTIAL_TOKENS)

    return (has_request_verb and has_credential_object) or bare_credential


async def credential_guard_node(state: ChatState) -> ChatState:
    """Rechaza de forma determinista las peticiones de credenciales.

    Si el mensaje pide JWT/token/contraseña/credenciales, fija la respuesta de
    seguridad y marca ``guard_triggered`` para que el grafo salte directo a la
    auditoría de salida (sin razonamiento LLM ni fallback de catálogo). En caso
    contrario deja ``guard_triggered`` en ``False`` explícitamente para que el
    estado del turno sea determinista.
    """
    if _requests_credentials(state.message):
        state.guard_triggered = True
        state.response = GUARD_RESPONSE
    else:
        state.guard_triggered = False
    return state
