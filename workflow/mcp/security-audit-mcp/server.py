import os

from mcp.server import FastMCP

mcp = FastMCP("Security-Audit-MCP")

DATABASE_PATH = os.getenv("DATABASE_PATH", "../database/BibliotecaVirtual.db")


@mcp.tool()
def ping() -> str:
    return "pong"


if __name__ == "__main__":
    mcp.run()
