"""Prueba e2e de conversación fluida del chatbot (US-026).

Requiere el stack vivo (backend + chatbot) y las credenciales del ``.env``
(``ADMIN_EMAIL``/``ADMIN_PASSWORD``) para autenticar contra el backend.

Aislada con el marker ``e2e`` (ver ``pytest.ini``) para no ejecutarse en el run
de unidades por defecto. Se ``skip`` con mensaje claro si faltan variables.

Sin credenciales hardcodeadas: se leen exclusivamente de variables de entorno.
No se loguean ni la contraseña ni el JWT.
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

FAREWELL_MARKERS = (
    "vuelve cuando quieras",
    "que tengas un excelente día",
    "hasta pronto",
    "adiós",
    "chao",
    "nos vemos",
)


def _no_farewell(text: str) -> bool:
    lowered = (text or "").lower()
    return not any(marker in lowered for marker in FAREWELL_MARKERS)


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        pytest.skip(
            f"'{name}' no está definida en el entorno/.env: "
            "la prueba e2e requiere el stack vivo y las credenciales del .env."
        )
    return value


@pytest.mark.e2e
async def test_e2e_fluid_conversation():
    """Login con .env + "hola" + seguimiento en la misma conversación.

    Verifica que:
    1. La autenticación contra el backend funciona (JWT + user.id).
    2. Un saludo "hola" responde de forma abierta (NO despedida).
    3. El seguimiento responde en el mismo conversationId (hilo continuo).
    """
    api_base = _env("VITE_API_BASE_URL")
    chatbot_base = _env("VITE_CHATBOT_API_BASE_URL")
    admin_email = _env("ADMIN_EMAIL")
    admin_password = _env("ADMIN_PASSWORD")

    # 1. Autenticación
    async with httpx.AsyncClient(timeout=30) as client:
        login_resp = await client.post(
            f"{api_base}/api/auth/login",
            json={"email": admin_email, "password": admin_password},
        )
    assert login_resp.status_code == 200, (
        f"Login falló con status {login_resp.status_code}: {login_resp.text}"
    )
    auth = login_resp.json()
    access_token = auth.get("accessToken")
    user_id = (auth.get("user") or {}).get("id")
    assert access_token, "El login no devolvió accessToken"
    assert user_id, "El login no devolvió user.id"

    # 2/3. Conversación en un conversationId limpio
    conversation_id = f"e2e-{uuid.uuid4()}"
    headers = {"Authorization": f"Bearer {access_token}", "X-Correlation-ID": f"e2e-{uuid.uuid4()}"}

    async with httpx.AsyncClient(timeout=120) as client:
        # Saludo: debe abrir, no despedirse
        hello_resp = await client.post(
            f"{chatbot_base}/chat",
            json={
                "message": "hola",
                "userId": user_id,
                "conversationId": conversation_id,
            },
            headers=headers,
        )
        assert hello_resp.status_code == 200, (
            f"/chat (hola) falló con status {hello_resp.status_code}: {hello_resp.text}"
        )
        hello = hello_resp.json()
        assert hello.get("conversation_id") == conversation_id, (
            "El chat no devolvió el mismo conversationId (se reinició el hilo)."
        )
        hello_msg = hello.get("message") or ""
        assert hello_msg.strip(), "El saludo no generó respuesta."
        assert _no_farewell(hello_msg), (
            f"El saludo respondió con una despedida (conversación cerrada): {hello_msg!r}"
        )

        # Seguimiento: continúa el hilo en la misma conversación
        follow_resp = await client.post(
            f"{chatbot_base}/chat",
            json={
                "message": "¿qué me recomiendas?",
                "userId": user_id,
                "conversationId": conversation_id,
            },
            headers=headers,
        )
        assert follow_resp.status_code == 200, (
            f"/chat (seguimiento) falló con status {follow_resp.status_code}: {follow_resp.text}"
        )
        follow = follow_resp.json()
        assert follow.get("conversation_id") == conversation_id, (
            "El seguimiento reinició la conversación (conversationId distinto)."
        )
        follow_msg = follow.get("message") or ""
        assert follow_msg.strip(), "El seguimiento no generó respuesta."
