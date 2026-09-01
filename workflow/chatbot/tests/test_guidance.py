"""Tests de la intención ``guidance`` (US-021 item 1, ADR-040).

El chatbot guía a un lector principiante de forma conversacional usando SOLO
libros reales del catálogo (nunca inventa títulos), con fallback heurístico si
el LLM no está disponible y sin regresión sobre smalltalk (US-020).
"""

import pytest

from app.graph.state import ChatState


def normalize(raw: dict) -> ChatState:
    defaults = ChatState(message=raw.get("message") or "")
    for field in defaults.__dataclass_fields__:
        if field in raw:
            setattr(defaults, field, raw[field])
    return defaults


@pytest.mark.asyncio
async def test_beginner_reader_message_classifies_as_guidance(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client

    async def fake_preferences(user_id):
        return []

    async def fake_search(query, limit=10):
        return [{"title": "El principito", "author": "Saint-Exupéry", "genre": "Novela"}]

    async def fake_llm(context):
        return None  # LLM no disponible -> fallback heurístico

    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", fake_preferences)
    monkeypatch.setattr(biblioteca_client, "buscar_libros", fake_search)
    monkeypatch.setattr(llm_client, "generate_guidance", fake_llm)

    state = ChatState(message="Soy un lector principiante. Me gustaría que me guíes", user_id="user-1")
    result = normalize(await graph_ainvoke(state))

    assert result.intent == "guidance"
    assert result.response
    # Nunca cae en el fallback de catálogo.
    assert "no hemos encontrado" not in result.response.lower()


@pytest.mark.asyncio
async def test_guidance_uses_real_catalog_matches(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client

    catalog = [
        {"title": "Rayuela", "author": "Cortázar", "genre": "Novela"},
        {"title": "Don Quijote", "author": "Cervantes", "genre": "Clásicos"},
    ]

    async def fake_preferences(user_id):
        return [{"id": "p1", "genre": "Novela"}]

    async def fake_search(query, limit=10):
        return catalog

    async def fake_llm(context):
        return None

    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", fake_preferences)
    monkeypatch.setattr(biblioteca_client, "buscar_libros", fake_search)
    monkeypatch.setattr(llm_client, "generate_guidance", fake_llm)

    state = ChatState(message="no sé qué leer, guíame", user_id="user-1")
    result = normalize(await graph_ainvoke(state))

    assert result.intent == "guidance"
    assert "Rayuela" in result.response
    assert "Don Quijote" in result.response


@pytest.mark.asyncio
async def test_guidance_fallback_when_llm_unavailable(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client

    async def fake_preferences(user_id):
        return [{"id": "p1", "genre": "Fantasía"}]

    async def fake_search(query, limit=10):
        return [{"title": "El nombre del viento", "author": "Rothfuss", "genre": "Fantasía"}]

    async def fake_llm(context):
        return None  # simulamos LLM caído

    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", fake_preferences)
    monkeypatch.setattr(biblioteca_client, "buscar_libros", fake_search)
    monkeypatch.setattr(llm_client, "generate_guidance", fake_llm)

    state = ChatState(message="quiero empezar a leer fantasía", user_id="user-1")
    result = normalize(await graph_ainvoke(state))

    assert result.intent == "guidance"
    # El fallback usa el catálogo real y no colapsa.
    assert "El nombre del viento" in result.response


@pytest.mark.asyncio
async def test_guidance_does_not_invent_titles(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client

    async def fake_preferences(user_id):
        return []

    async def fake_search(query, limit=10):
        # Catálogo vacío: la guía NO debe inventar títulos.
        return []

    async def fake_llm(context):
        return None

    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", fake_preferences)
    monkeypatch.setattr(biblioteca_client, "buscar_libros", fake_search)
    monkeypatch.setattr(llm_client, "generate_guidance", fake_llm)

    state = ChatState(message="guíame como lector principiante", user_id="user-1")
    result = normalize(await graph_ainvoke(state))

    assert result.intent == "guidance"
    # Sin coincidencias reales no debe citar ningún título concreto.
    assert not any(t.startswith("- «") for t in result.response.splitlines())
    assert result.response


@pytest.mark.asyncio
async def test_greeting_still_smalltalk(monkeypatch):
    """Regresión US-020: un saludo simple sigue siendo smalltalk, no guidance."""
    import app.mcp_clients.biblioteca_client as biblioteca_client

    async def fake_state(user_id):
        return "sin_actividad"

    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", fake_state)

    state = ChatState(message="hola!", user_id="user-1")
    result = normalize(await graph_ainvoke(state))

    assert result.intent == "other"


@pytest.mark.asyncio
async def test_guidance_mcp_unavailable_fallback(monkeypatch):
    """Un fallo de Biblioteca-MCP no colapsa la guía (degradación a [])."""
    from app.graph.build_graph import graph

    # conftest ya hace fallar biblioteca_client -> el guidance usa fallback general.
    state = ChatState(message="soy novato, guíame", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.intent == "guidance"
    assert result.response


async def graph_ainvoke(state: ChatState):
    from app.graph.build_graph import graph

    return await graph.ainvoke(state)
