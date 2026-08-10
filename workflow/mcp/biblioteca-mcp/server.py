import os
import sys
from pathlib import Path

from mcp.server import FastMCP

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "workflow" / "mcp"))

from common.settings import get_database_path

mcp = FastMCP("Biblioteca-MCP")

DATABASE_PATH = get_database_path()


@mcp.tool()
def ping() -> str:
    return "pong"


if __name__ == "__main__":
    mcp.run()
