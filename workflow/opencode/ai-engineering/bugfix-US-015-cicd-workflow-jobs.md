# AI Engineering Log — bugfix-US-015-cicd-workflow-jobs

**Story:** US-015 — Fix CI/CD: definir VITE_API_BASE_URL y VITE_CHATBOT_API_BASE_URL en el job frontend del workflow GitHub Actions y agregar al proceso las aplicaciones faltantes
**Branch:** `bugfix/US-015-cicd-workflow-jobs`
**Role:** Technical Lead (consolidación); Frontend Developer, AI Engineer, Backend Developer, QA, Technical Writer (planes y validación)

## Iteration 1 — Implementación

### Contexto
- El pipeline `.github/workflows/ci.yml` solo validaba `backend` y `frontend`. El fail-fast de US-014 (ADR-025) rompió el job `frontend` en CI porque el workflow no definía `VITE_API_BASE_URL` ni `VITE_CHATBOT_API_BASE_URL` (evidencia: `Error_CICD.txt`).
- El chatbot (FastAPI) y los MCP (Biblioteca-MCP, Security-Audit-MCP, Open Library MCP) no tenían validación en CI pese a disponer de suites pytest autocontenidas.

### Cambios
1. **`.github/workflows/ci.yml`**
   - Job `frontend`: añadido bloque `env:` al paso `npm run build` con `VITE_API_BASE_URL: http://localhost:5000` y `VITE_CHATBOT_API_BASE_URL: http://localhost:8000` (valores de build-time de CI, no secretos).
   - Job `backend`: eliminado `dotnet test --no-build --configuration Release || true` (no existen proyectos de test en `workflow/backend`; era un falso verde silencioso).
   - Nuevo job `python`: setup-python 3.12, `pip install -r` de los 4 requirements (chatbot, biblioteca-mcp, open-library-mcp, security-audit-mcp) y `pytest` sobre las suites de chatbot, Biblioteca-MCP y Open Library MCP. Cada suite corre desde su directorio de módulo (`working-directory`) porque el conftest del chatbot resuelve el paquete `app` relativo a la raíz del módulo (el comando único desde la raíz del repo falla en la recolección).
2. **`README.md` raíz**: nueva sección «12. CI/CD» describiendo los 3 jobs y las variables que CI inyecta.
3. **`DECISIONS.md`**: nuevo ADR-028 «CI coverage of the whole stack with fail-fast config».
4. **Housekeeping (solicitado por el usuario antes de la aprobación):** `verify_seed_open_library.py` movido de `workflow/scripts/` a `workflow/mcp/open-library-mcp/` (pertenece al módulo Open Library MCP), con corrección de `REPO_ROOT` (ahora `parents[3]`); `.pytest_cache` huérfano de la raíz de `workflow/` consolidado en `workflow/mcp/open-library-mcp/.pytest_cache/`; referencias de ruta actualizadas en `README.md`, `DECISIONS.md` (ADR-020), `US-010.md` y la bitácora de US-010.

### Validación ejecutada
- `dotnet build --no-restore --configuration Release` en `workflow/backend`: Build succeeded, 0 warnings, 0 errors.
- `find workflow/backend -iname '*test*'`: sin proyectos de test (confirma eliminar el paso `dotnet test || true`).
- `VITE_API_BASE_URL=http://localhost:5000 VITE_CHATBOT_API_BASE_URL=http://localhost:8000 npm run build` en `workflow/frontend`: éxito (exit 0).
- `npm run build` sin las variables: exit 1 (fail-fast de US-014 se conserva).
- `python -m pytest tests` desde `workflow/chatbot`: 40 passed.
- `python -m pytest tests` desde `workflow/mcp/biblioteca-mcp`: 12 passed.
- `python -m pytest tests` desde `workflow/mcp/open-library-mcp`: 13 passed.
- Total: 65 tests pasan, sin red ni API keys.
- Validación YAML de `.github/workflows/ci.yml` (PyYAML): OK; 3 jobs presentes; env del job frontend presente.

### Resultado
Implementación completada. Estado avanzado a `Implemented` vía MCP. Pendiente: QA (`qa-check US-015`).

## Iteración 2 — QA formal (`qa-check US-015`)

### Contexto
- QA ejecutado sobre `bugfix/US-015-cicd-workflow-jobs` (`5ff6ab7`) con `index_repository` previo (2881 nodos / 6007 edges indexados).
- Estado MCP verificado: `Implemented`.

### Validación de criterios de aceptación
1. **Frontend con env:** `.github/workflows/ci.yml` job `frontend` define `VITE_API_BASE_URL=http://localhost:5000` y `VITE_CHATBOT_API_BASE_URL=http://localhost:8000` en el paso `npm run build` (parse YAML OK). `npm run build` con env → exit 0; sin env → exit 1 (fail-fast conservado).
2. **Job python:** presente con los 4 `pip install -r` y pytest por módulo (`working-directory`). pytest chatbot 40 + biblioteca-mcp 12 + open-library-mcp 13 = 65 passed, sin red ni secretos.
3. **Stack completo:** 3 jobs (`backend`, `frontend`, `python`). `dotnet build --no-restore --configuration Release` → Build succeeded, 0 warnings/0 errors.

### Resultado QA
**PASS.** Documentation Gate cumplido (US-015.md + esta bitácora). PR hacia `main` creado vía GitHub MCP `create_pull_request`. Estado avanzado a `Validated` vía MCP.