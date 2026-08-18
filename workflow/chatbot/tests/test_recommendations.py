import pytest

from app.graph.build_graph import graph
from app.graph.state import ChatState


def normalize(raw: dict) -> ChatState:
    defaults = ChatState(message=raw.get("message") or "")
    for field in defaults.__dataclass_fields__:
        if field in raw:
            setattr(defaults, field, raw[field])
    return defaults


@pytest.mark.asyncio
async def test_recommendation_by_history(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client

    async def fake_preferences(user_id):
        return [{"id": "p1", "genre": "Novela"}]

    async def fake_recommendations(user_id, limit=5):
        return [
            {
                "id": "b1",
                "title": "Cien años de soledad",
                "author": "García Márquez",
                "genre": "Novela",
                "available_copies": 2,
                "reason": "coincide con tus preferencias",
            },
            {
                "id": "b2",
                "title": "Rayuela",
                "author": "Cortázar",
                "genre": "Novela",
                "available_copies": 0,
                "reason": "coincide con tu historial",
            },
        ]

    async def fake_llm(context):
        return None  # LLM no disponible -> fallback heurístico

    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", fake_preferences)
    monkeypatch.setattr(biblioteca_client, "listar_recomendaciones_por_genero", fake_recommendations)
    monkeypatch.setattr(llm_client, "generate_recommendation", fake_llm)

    state = ChatState(message="recomiéndame un libro", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.intent == "recommendation"
    assert len(result.recommendations) == 1  # solo el disponible
    assert result.recommendations[0]["id"] == "b1"
    assert "recomiendo" in result.response.lower()
    assert "Cien años de soledad" in result.response


@pytest.mark.asyncio
async def test_recommendation_uses_llm_when_available(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client

    async def fake_preferences(user_id):
        return [{"id": "p1", "genre": "Novela"}]

    async def fake_recommendations(user_id, limit=5):
        return [
            {
                "id": "b1",
                "title": "Rayuela",
                "author": "Cortázar",
                "genre": "Novela",
                "available_copies": 1,
                "reason": "coincide con tus preferencias",
            }
        ]

    async def fake_llm(context):
        return "Te recomiendo Rayuela, una novela ideal para ti."

    monkeypatch.setattr(biblioteca_client, "obtener_preferencias", fake_preferences)
    monkeypatch.setattr(biblioteca_client, "listar_recomendaciones_por_genero", fake_recommendations)
    monkeypatch.setattr(llm_client, "generate_recommendation", fake_llm)

    state = ChatState(message="¿qué me recomiendas?", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.llm_used is True
    assert "Rayuela" in result.response


@pytest.mark.asyncio
async def test_feedback_saved(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client

    async def fake_search(message, limit=10):
        return [{"id": "b1", "title": "Rayuela", "author": "Cortázar"}]

    async def fake_register(user_id, book_id, rating, comment=None):
        assert book_id == "b1"
        assert rating == 5
        return {"success": True, "message": "ok"}

    monkeypatch.setattr(biblioteca_client, "buscar_libros", fake_search)
    monkeypatch.setattr(biblioteca_client, "registrar_feedback", fake_register)

    state = ChatState(message="me gustó Rayuela", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.intent == "feedback"
    assert "valoración" in result.response.lower() or "gracias" in result.response.lower()


@pytest.mark.asyncio
async def test_due_reminder(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client

    async def fake_estado(user_id):
        return "por_vencer"

    async def fake_en_curso(user_id):
        return {"id": "r1", "book_id": "b1", "title": "Rayuela", "due_date": "2026-08-20"}

    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", fake_estado)
    monkeypatch.setattr(biblioteca_client, "consultar_libro_en_curso", fake_en_curso)

    state = ChatState(message="mis alquileres", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.intent == "status"
    assert "por vencer" in result.response.lower()
    assert "Rayuela" in result.response


@pytest.mark.asyncio
async def test_overdue(monkeypatch):
    import app.mcp_clients.biblioteca_client as biblioteca_client

    async def fake_estado(user_id):
        return "vencido"

    async def fake_en_curso(user_id):
        return {"id": "r1", "book_id": "b1", "title": "La ciudad", "due_date": "2026-07-01"}

    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", fake_estado)
    monkeypatch.setattr(biblioteca_client, "consultar_libro_en_curso", fake_en_curso)

    state = ChatState(message="estado de lectura", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.intent == "status"
    assert "vencido" in result.response.lower()


@pytest.mark.asyncio
async def test_recommendation_mcp_unavailable_fallback(monkeypatch):
    """Biblioteca-MCP caído no debe colapsar la recomendación."""
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.mcp_clients.security_audit_client as security_client

    async def fake_audit_input(text, correlation_id=None):
        return {"safe": True}

    async def fake_audit_output(text, correlation_id=None):
        return {"safe": True}

    async def fake_estado(user_id):
        return "sin_actividad"

    # Todos los métodos de Biblioteca-MCP fallan (conftest) salvo get_estado_lectura
    monkeypatch.setattr(security_client, "audit_input", fake_audit_input)
    monkeypatch.setattr(security_client, "audit_output", fake_audit_output)
    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", fake_estado)

    state = ChatState(message="recomiéndame un libro", user_id="user-1")
    result = normalize(await graph.ainvoke(state))

    assert result.intent == "recommendation"
    assert result.recommendations == []
    assert result.response  # respuesta amable sin colapso


@pytest.mark.asyncio
async def test_output_audited_and_correlation_id(monkeypatch):
    captured = {}

    async def fake_audit_input(text, correlation_id=None):
        captured["input_corr"] = correlation_id
        return {"safe": True}

    async def fake_audit_output(text, correlation_id=None):
        captured["output_corr"] = correlation_id
        captured["output_text"] = text
        return {"safe": True}

    import app.mcp_clients.security_audit_client as security_client

    monkeypatch.setattr(security_client, "audit_input", fake_audit_input)
    monkeypatch.setattr(security_client, "audit_output", fake_audit_output)

    state = ChatState(message="¿Tienen Rayuela?", correlation_id="corr-123")
    result = normalize(await graph.ainvoke(state))

    assert captured["input_corr"] == "corr-123"
    assert captured["output_corr"] == "corr-123"
    assert captured["output_text"] == result.response
    assert result.response
