FROM python:3.12-slim
WORKDIR /app

# Dependencias del chatbot (build context = raíz del repo)
COPY workflow/chatbot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Dependencias de los tres servidores MCP empaquetados en la imagen
COPY workflow/mcp/biblioteca-mcp/requirements.txt /app/workflow/mcp/biblioteca-mcp/requirements.txt
COPY workflow/mcp/open-library-mcp/requirements.txt /app/workflow/mcp/open-library-mcp/requirements.txt
COPY workflow/mcp/security-audit-mcp/requirements.txt /app/workflow/mcp/security-audit-mcp/requirements.txt
RUN pip install --no-cache-dir -r /app/workflow/mcp/biblioteca-mcp/requirements.txt -r /app/workflow/mcp/open-library-mcp/requirements.txt -r /app/workflow/mcp/security-audit-mcp/requirements.txt

# Código del chatbot y de los MCP.
# IMPORTANTE: se preserva la ruta /app/workflow/mcp/<server>/server.py para que
# el bootstrap Path(__file__).resolve().parents[3] + sys.path.insert(0,
# REPO_ROOT / "workflow" / "mcp") de los servidores MCP siga resolviendo.
COPY workflow/chatbot /app
COPY workflow/mcp /app/workflow/mcp

EXPOSE 8000
CMD ["sh", "-c", "python -m app.startup_checks && exec uvicorn main:app --host \"$HOST\" --port \"$PORT\""]
