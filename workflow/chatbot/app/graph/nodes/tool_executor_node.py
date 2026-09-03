from __future__ import annotations

from typing import Any, Callable, Coroutine

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client

# Registro determinista de tools de Biblioteca-MCP (solo lectura, ADR-011).
#
# Diseño híbrido (US-027): el LLM SOLO sugiere NOMBRES de herramientas durante la
# clasificación (state.suggested_tools). La EJECUCIÓN es determinista desde este
# nodo del grafo — nunca es una elección libre del LLM. Esto mantiene el control
# del flujo en LangGraph y evita llamadas arbitrarias/agentic a herramientas
# durante la clasificación (ver seguridad en SKILL mcp-tools).
_TOOL_REGISTRY: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {
    "buscar_libros": biblioteca_client.buscar_libros,
    "obtener_preferencias": biblioteca_client.obtener_preferencias,
    "listar_recomendaciones_por_genero": biblioteca_client.listar_recomendaciones_por_genero,
    "get_estado_lectura": biblioteca_client.get_estado_lectura,
    "consultar_alquileres_usuario": biblioteca_client.consultar_alquileres_usuario,
}

# Herramientas que requieren un user_id autenticado para ejecutarse.
_USER_SCOPED_TOOLS = frozenset({
    "obtener_preferencias",
    "listar_recomendaciones_por_genero",
    "get_estado_lectura",
    "consultar_alquileres_usuario",
})


def _needs_user_id(tool_name: str) -> bool:
    return tool_name in _USER_SCOPED_TOOLS


async def execute_tool(tool_name: str, state: ChatState) -> dict[str, Any]:
    """Ejecuta una tool de Biblioteca-MCP de forma determinista.

    Los fallos individuales nunca rompen el turno: se registra un resultado con
    ``ok=False`` (ADR-023, "handle MCP failures gracefully").
    """
    invoker = _TOOL_REGISTRY.get(tool_name)
    if invoker is None:
        return {
            "tool": tool_name,
            "ok": False,
            "error": f"Tool '{tool_name}' desconocida.",
        }

    try:
        if _needs_user_id(tool_name):
            if not state.user_id:
                return {
                    "tool": tool_name,
                    "ok": False,
                    "error": "Usuario no identificado; no se pudo ejecutar la herramienta.",
                }
            result = await invoker(state.user_id)
        else:
            result = await invoker(state.query or state.message)
        return {"tool": tool_name, "ok": True, "result": result}
    except Exception as exc:  # noqa: BLE001 - fallback elegante (ADR-023)
        return {"tool": tool_name, "ok": False, "error": str(exc)}


async def tool_executor_node(state: ChatState) -> ChatState:
    """Ejecuta las tools sugeridas por el LLM y almacena sus resultados planos.

    Nodo determinista controlado por el grafo: NO deja que el LLM llame
    herramientas arbitrariamente. Solo ejecuta las sugerencias validadas de
    ``state.suggested_tools`` (0-2, generadas por ``llm_classify_node`` a partir
    del prompt de clasificación). Los resultados se guardan en
    ``state.tool_results`` para consumo de los nodos especializados y del
    ``response_node`` (US-027 diseño híbrido).
    """
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for tool_name in state.suggested_tools or []:
        if tool_name in seen:
            continue
        seen.add(tool_name)
        results.append(await execute_tool(tool_name, state))
    state.tool_results = results
    return state
