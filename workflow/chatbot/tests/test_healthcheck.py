"""Tests del script de healthcheck para Docker Compose (app/healthcheck.py, US-023).

Herméticos: se parchea ``urllib.request.urlopen`` para simular HTTP 200, 503 y
errores de red sin levantar el servidor.
"""

from __future__ import annotations

import urllib.error

import pytest

import app.healthcheck as healthcheck


class _FakeUrlResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        return None


def _patch_urlopen(monkeypatch, *responses):
    """Sustituye urlopen por un fake que devuelve respuestas en orden o lanza."""
    remaining = list(responses)
    calls = []

    def _fake(url, timeout=None):
        calls.append((url, timeout))
        if not remaining:
            raise AssertionError("urlopen llamado más veces de las esperadas")
        item = remaining.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(urllib.request, "urlopen", _fake)
    return calls


def test_probe_exit_zero_when_200(monkeypatch):
    """(a) /health 200 -> probe() devuelve 0."""
    calls = _patch_urlopen(monkeypatch, _FakeUrlResponse(200))
    assert healthcheck.probe() == 0
    assert calls[0][0] == healthcheck.HEALTH_URL


def test_probe_exit_one_when_503(monkeypatch):
    """(b) /health 503 -> probe() devuelve 1 (degraded)."""
    _patch_urlopen(monkeypatch, _FakeUrlResponse(503))
    assert healthcheck.probe() == 1


def test_probe_exit_one_when_unreachable(monkeypatch):
    """(c) URL inalcanzable (URLError) -> probe() devuelve 1."""
    _patch_urlopen(monkeypatch, urllib.error.URLError("connection refused"))
    assert healthcheck.probe() == 1


def test_probe_exit_one_on_os_error(monkeypatch):
    """(d) OSError/Timeout -> probe() devuelve 1."""
    _patch_urlopen(monkeypatch, OSError("timed out"))
    assert healthcheck.probe() == 1


@pytest.mark.parametrize("status", [200, 503])
def test_probe_exit_matches_status(monkeypatch, status):
    """(e) Exit code coherente con el estado HTTP (200->0, 503->1)."""
    _patch_urlopen(monkeypatch, _FakeUrlResponse(status))
    assert healthcheck.probe() == (0 if status == 200 else 1)