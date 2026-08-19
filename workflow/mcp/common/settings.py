"""Configuración compartida para los servidores MCP del repositorio.

Solo usa la biblioteca estándar (``os``, ``pathlib``, ``functools``) para no
acoplar los MCP a dependencias externas. La ruta de la base de datos se lee de
la variable de entorno ``DATABASE_PATH`` (obligatoria) y se resuelve de forma
absoluta contra la raíz del repositorio.
"""

import os
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def require_env(name: str) -> str:
    """Devuelve el valor de una variable de entorno requerida (fail-fast).

    Raises:
        RuntimeError: si la variable no está definida o está vacía.
    """
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno requerida '{name}' "
            f"para configurar el servidor MCP."
        )
    return value


@lru_cache(maxsize=1)
def get_database_path(env_name: str = "DATABASE_PATH", base_dir: Path | None = None) -> Path:
    """Devuelve la ruta absoluta de la base de datos SQLite.

    - ``DATABASE_PATH`` es obligatoria: si está vacía o ausente, se lanza
      ``RuntimeError`` con el nombre de la variable.
    - Las rutas relativas se resuelven contra ``base_dir`` (por defecto, la
      raíz del repositorio), corrigiendo rutas rotas tipo ``../database/...``.
    - Valida que el directorio padre exista y lanza ``FileNotFoundError`` con
      la ruta absoluta si no es así.
    """
    raw_value = require_env(env_name)
    candidate = Path(raw_value).expanduser()

    base = base_dir or REPO_ROOT
    database_path = candidate if candidate.is_absolute() else (base / candidate)
    database_path = database_path.resolve()

    parent = database_path.parent
    if not parent.is_dir():
        raise FileNotFoundError(
            f"El directorio de la base de datos no existe: {parent}. "
            f"Revise la variable de entorno '{env_name}' (actual: '{raw_value}')."
        )

    return database_path


def clear_settings_cache() -> None:
    get_database_path.cache_clear()
