"""Configuración compartida para los servidores MCP del repositorio.

Solo usa la biblioteca estándar (``os``, ``pathlib``, ``functools``) para no
acoplar los MCP a dependencias externas. La ruta de la base de datos se lee de
la variable de entorno ``DATABASE_PATH`` (o el valor por defecto) y se resuelve
de forma absoluta contra la raíz del repositorio.
"""

import os
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DATABASE_PATH = REPO_ROOT / "workflow" / "database" / "BibliotecaVirtual.db"


@lru_cache(maxsize=1)
def get_database_path(env_name: str = "DATABASE_PATH", base_dir: Path | None = None) -> Path:
    """Devuelve la ruta absoluta de la base de datos SQLite.

    - Un ``DATABASE_PATH`` vacío o ausente se trata como no definido y se usa
      el valor por defecto.
    - Las rutas relativas se resuelven contra ``base_dir`` (por defecto, la
      raíz del repositorio), corrigiendo rutas rotas tipo ``../database/...``.
    - Valida que el directorio padre exista y lanza ``FileNotFoundError`` con
      la ruta absoluta si no es así.
    """
    raw_value = os.getenv(env_name, "")
    candidate = Path(raw_value).expanduser() if raw_value else DEFAULT_DATABASE_PATH

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
