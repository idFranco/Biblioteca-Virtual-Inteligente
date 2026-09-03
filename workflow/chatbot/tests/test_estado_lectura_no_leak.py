"""Tests del fix de fuga de PII/tool-repr en el estado de lectura (US-029).

Part 1:
- ``get_estado_lectura`` extrae SOLO el ``estado`` de respuestas de
  Biblioteca-MCP en varias formas (dict, str-JSON, repr de ``CallToolResult``)
  sin exponer el ``user_id`` ni la serialización interna.
- ``response_node`` para intent ``status`` solo interpola estados whitelisteados
  y usa un fallback genérico ante valores inesperados (nunca reprs crudos).
"""

import pytest

from app.mcp_clients.biblioteca_client import _extract_estado
from app.graph.state import ChatState
from app.graph.nodes.response_node import response_node


@pytest.mark.asyncio
async def test_extract_estado_from_plain_dict():
    assert _extract_estado({"user_id": "u1", "estado": "sin_actividad"}) == "sin_actividad"


def test_extract_estado_from_json_string():
    assert (
        _extract_estado('{"user_id":"3acb4f67","estado":"en_curso"}') == "en_curso"
    )


def test_extract_estado_from_calltoolresult_repr_no_leak():
    """El repr crudo del SDK MCP debe resolverse al estado, sin filtrar user_id."""
    raw_repr = (
        "meta=None content=[TextContent(type='text', "
        "text='{\"user_id\":\"3acb4f67-3439-4d0d-a94e-892ddea034d7\","
        "\"estado\":\"sin_actividad\"}', annotations=None, meta=None)] "
        "structured_content={'user_id': '3acb4f67-3439-4d0d-a94e-892ddea034d7', "
        "'estado': 'sin_actividad'} is_error=False result_type='complete'"
    )
    result = _extract_estado(raw_repr)
    assert result == "sin_actividad"
    assert "3acb4f67" not in str(result)
    assert "TextContent" not in str(result)


def test_extract_estado_unknown_shape_returns_none():
    assert _extract_estado(None) is None
    assert _extract_estado(12345) is None
    assert _extract_estado(["no", 1, 2]) is None


@pytest.mark.asyncio
async def test_response_node_status_uses_label_for_valid_state():
    state = ChatState(message="¿cómo está mi alquiler?", intent="status", reading_state="por_vencer")
    result = await response_node(state)
    assert "por vencer" in result.response
    assert "por_vencer" not in result.response.replace("«por vencer»", "")


@pytest.mark.asyncio
async def test_response_node_status_uses_fallback_for_raw_value():
    """Un reading_state con repr crudo NO debe filtrarse en la respuesta."""
    state = ChatState(
        message="¿cómo está mi alquiler?",
        intent="status",
        reading_state=(
            "meta=None content=[TextContent(type='text', text='{\"user_id\":\""
            "3acb4f67-3439-4d0d-a94e-892ddea034d7\",\"estado\":\"sin_actividad\"}')]"
        ),
    )
    result = await response_node(state)
    assert "3acb4f67" not in result.response
    assert "TextContent" not in result.response
    assert "No pude recuperar tu estado de lectura" in result.response


@pytest.mark.asyncio
async def test_response_node_status_sin_actividad_label():
    state = ChatState(message="¿cómo está mi alquiler?", intent="status", reading_state="sin_actividad")
    result = await response_node(state)
    assert "sin actividad" in result.response