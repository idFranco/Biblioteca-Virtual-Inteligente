"""Nodo de guía conversacional para lectores principiantes (US-021 item 1).

Responde de forma conversacional a la intención ``guidance`` («soy un lector
principiante», «guíame», «no sé qué leer») en lugar de caer en el catch-all de
catálogo («No hemos encontrado «...» en el catálogo»).

Flujo:
1. Extrae un tema/género del mensaje (heurística ligera); si queda vacío, usa
   el género preferido del usuario (``obtener_preferencias``).
2. Consulta el catálogo real vía ``biblioteca_client.buscar_libros``.
3. Construye un contexto enmascarado (mensaje + preferencias + matches reales
   exponiendo solo title/author/genre) y lo envía al LLM con
   ``generate_guidance``.
4. Si el LLM no está disponible o falla, usa el fallback heurístico
   ``_guidance_fallback`` que referencia SOLO los títulos reales encontrados
   (nunca inventa, ADR-023).

Un fallo de Biblioteca-MCP no colapsa el grafo: las consultas se degradan a
``[]`` y la guía orienta de forma general.
"""

from __future__ import annotations

from app.graph.state import ChatState
from app.llm import client as llm_client
from app.mcp_clients import biblioteca_client
from app.utils.pii_masker import mask_message

# Géneros accesibles reconocidos en el mensaje del usuario (clave canónica →
# variantes). Se usan como tema de búsqueda en el catálogo real.
_GENRE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "fantasía": ("fantasía", "fantasia", "fantástico", "fantastico"),
    "ciencia ficción": ("ciencia ficción", "ciencia ficcion", "scifi", "sci-fi"),
    "novela": ("novela", "novelas"),
    "misterio": ("misterio", "misterios", "policial", "policiaca", "thriller"),
    "terror": ("terror", "horror"),
    "poesía": ("poesía", "poesia", "poemas", "poemario"),
    "romance": ("romance", "romántica", "romantica", "romántico", "romantico"),
    "histórica": ("histórica", "historica", "histórico", "historico"),
    "aventura": ("aventura", "aventuras"),
    "clásicos": ("clásicos", "clasicos", "clásica", "clasica", "clásico", "clasico"),
    "juvenil": ("juvenil", "infantil", "young adult"),
    "biografía": ("biografía", "biografia", "autobiografía", "autobiografia"),
}


def _extract_theme(message: str) -> str:
    """Extrae un tema/género del mensaje del usuario (heurística ligera).

    Returns:
        El género canónico si el mensaje menciona alguno conocido, o ``""``.
    """
    if not message:
        return ""
    lower = message.lower()
    for genre, keywords in _GENRE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower:
                return genre
    return ""


def _preferred_genre(preferences: list[dict]) -> str:
    """Devuelve el primer género preferido registrado del usuario, o ``""``."""
    for pref in preferences or []:
        genre = (pref.get("genre") or "").strip()
        if genre:
            return genre
    return ""


def _matches_text(matches: list[dict]) -> str:
    """Lista los libros reales del catálogo exponiendo solo title/author/genre."""
    lines = []
    for item in matches or []:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        author = (item.get("author") or "").strip()
        genre = (item.get("genre") or "").strip()
        line = f"- «{title}»"
        if author:
            line += f" de {author}"
        if genre:
            line += f" ({genre})"
        lines.append(line)
    return "\n".join(lines)


def _guidance_fallback(theme: str, matches: list[dict]) -> str:
    """Respuesta heurística de guía que referencia SOLO títulos reales.

    Nunca inventa títulos: si no hay coincidencias reales, orienta de forma
    general sin mencionar ningún libro concreto.
    """
    if not matches:
        if theme:
            return (
                f"¡Claro! Empezar a leer es un gran paso. Ahora mismo no tengo "
                f"libros de {theme} en el catálogo, pero puedo orientarte con "
                "otros títulos accesibles si me cuentas qué tipo de historias "
                "te gustan. También puedes explorar el catálogo cuando quieras."
            )
        return (
            "¡Claro! Empezar a leer es un gran paso. Cuéntame qué tipo de "
            "historias te gustan (aventuras, misterio, fantasía…) y te guiaré "
            "hacia los libros más accesibles de nuestro catálogo."
        )

    lines = []
    for item in matches[:3]:
        title = (item.get("title") or "").strip() or "un libro"
        author = (item.get("author") or "").strip()
        genre = (item.get("genre") or "").strip()
        detail = f"«{title}»" + (f" de {author}" if author else "")
        if genre:
            detail += f" ({genre})"
        lines.append(f"- {detail}")

    return (
        "¡Claro! Para empezar a leer te sugiero estos títulos de nuestro "
        "catálogo, que suelen ser muy accesibles:\n"
        + "\n".join(lines)
        + "\n\n¿Quieres que te cuente más sobre alguno o prefieres otro género?"
    )


async def guidance_node(state: ChatState) -> ChatState:
    """Guía conversacional para lectores principiantes (US-021 item 1).

    Extrae un tema del mensaje (o usa el género preferido del usuario),
    consulta el catálogo real vía Biblioteca-MCP y genera una respuesta de
    orientación con el LLM. Si el LLM no está disponible, usa un fallback
    heurístico que referencia SOLO los títulos reales encontrados (nunca
    inventa). Un fallo del MCP no colapsa el grafo.
    """
    message = state.message or ""

    preferences: list[dict] = []
    try:
        preferences = await biblioteca_client.obtener_preferencias(state.user_id)
    except Exception:
        preferences = []
    state.preferences = preferences

    theme = _extract_theme(message) or _preferred_genre(preferences)

    matches: list[dict] = []
    try:
        matches = await biblioteca_client.buscar_libros(theme, limit=10)
    except Exception:
        matches = []

    prefs_text = ", ".join(
        (pref.get("genre") or "").strip()
        for pref in preferences
        if (pref.get("genre") or "").strip()
    ) or "sin preferencias registradas"

    context_text = (
        f"Mensaje del usuario: {mask_message(message, state.user_id)}\n"
        f"Preferencias del usuario: {prefs_text}\n"
        f"Libros reales del catálogo:\n{_matches_text(matches) or 'Sin coincidencias en el catálogo.'}"
    )

    generated = await llm_client.generate_guidance(context_text)
    if generated:
        state.response = generated
        state.llm_used = True
    else:
        state.response = _guidance_fallback(theme, matches)
    return state