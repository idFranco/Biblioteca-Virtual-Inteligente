"""Probe síncrono para el healthcheck de Docker Compose (US-023).

Consulta ``GET /health`` del chatbot con ``urllib.request`` (stdlib; la imagen
``python:3.12-slim`` no incluye ``curl``) y sale:
- 0 si responde HTTP 200 (healthy).
- 1 si responde 503 (degraded) o si el endpoint es inalcanzable.

Uso: ``python -m app.healthcheck`` (test del healthcheck del servicio ``chatbot``).
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request

HEALTH_URL = "http://127.0.0.1:8000/health"


def probe() -> int:
    """Devuelve el código de salida del healthcheck (0 healthy, 1 otherwise)."""
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=5) as response:
            status = response.status
    except (urllib.error.URLError, OSError) as exc:
        print(f"[healthcheck] ERROR: no se pudo alcanzar {HEALTH_URL} ({exc})", file=sys.stderr)
        return 1

    if status == 200:
        print("[healthcheck] OK: /health responde 200")
        return 0
    print(f"[healthcheck] DEGRADED: /health responde HTTP {status}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(probe())