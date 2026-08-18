# AI Engineering — Bitácora de iteración — US-012 (rama `feature/US-012-chatbot-recommendations`)

## Iteración 1 — Implementación inicial

- Story `Approved → In Progress`; rama `feature/US-012-chatbot-recommendations` creada vía GitHub MCP.
- **Backend (solo esquema, `EnsureCreated`):** `Feedback.cs` y `UserPreference.cs` en `Domain/Entities`; `BibliotecaDbContext` ampliado con `DbSet<Feedback>`/`DbSet<UserPreference>` y configuraciones de relación/índices (FK User/Book → Feedback, User → UserPreference, índice único `(UserId, Genre)`). Sin endpoints ni handlers CQRS. Migración del proyecto a `net9.0` con paquetes `9.0.18` y Dockerfile `sdk:9.0.316`/`aspnet:9.0.18` por decisión del usuario (SDK local 9.0.316; `aspnet:9.0.316` no existe). `dotnet build` OK (0/0).
- **Biblioteca-MCP (`server.py`):** 5 herramientas nuevas — `consultar_alquileres_usuario`, `consultar_libro_en_curso`, `obtener_preferencias`, `listar_recomendaciones_por_genero` (solo libros con `AvailableCopies > 0`, con `reason` por preferencia/historial) y `registrar_feedback` (escritura acotada; `common/sqlite.py::execute`). Límite de escritura respetado.
- **Chatbot (LangGraph + LangChain):**
  - `state.py`: `preferences`, `recommendations`, `due_reminder_flag`, `feedback_payload`, `llm_used`.
  - Nuevos nodos: `route_by_state`, `preferences_node`, `due_reminder_node`, `overdue_node`, `feedback_node`, `save_feedback_node`, `llm_response_node`; actualizados `classify_intent_node` (feedback), `internal_catalog_node` (recomendación por historial/preferencias), `availability_node` (excluye sin copias), `response_node` y `load_user_state_node` (fallback MCP).
  - Grafo recompilado con auditoría obligatoria entrada/salida (Security-Audit-MCP) y enrutado por `route_by_state`.
  - `app/llm/client.py`: ChatOpenAI (LangChain) con `LLM_API_KEY`/`LLM_MODEL`, PII masking (`app/utils/pii_masker.py`) y fallback a `None` → respuesta heurística. Prompt en `app/prompts/recommendation_prompt.txt`.
  - `biblioteca_client.py`: 5 métodos nuevos para las herramientas MCP; `schemas.py`: `BookRecommendation` + `ChatResponse.recommendations`.
- **Frontend (frontend-ui-ux):** `chat.ts` con tipos `BookRecommendation`/`recommendations`; `ChatWidget.tsx` con tarjetas de recomendación (portada `BookCover` + fallback ornamental, badge de disponibilidad olive/oxide, razón) y botones «Me gustó»/«No me gustó» que envían mensaje de seguimiento al chatbot (nunca MCP directo, ADR-007). `npm run build` y `npm run lint` OK.
- Tests: chatbot `40 passed`; Biblioteca-MCP `12 passed` (fixture SQLite temporal). Base de desarrollo regenerada (borrado único documentado): tablas `Feedbacks` y `UserPreferences` creadas, seed de 50 libros intacto.
- Push vía MCP (`0e88eef`); story → `Implemented`; FINAL PUSH con notas de implementación (`cdc08f5`).

## Risk Register

| Risk | Nivel | Estado | Mitigación aplicada |
|---|---|---|---|
| Dependencia del LLM externo (latencia/indisponibilidad) | Alta | Mitigated | `llm_response_node` con timeout 20s y fallback silencioso a respuesta heurística; sin bloqueo del grafo. |
| Escritura de feedback vía Biblioteca-MCP rompe «solo lectura» | Media | Mitigated | Escritura acotada exclusivamente a `registrar_feedback`; resto de herramientas de solo lectura. |
| El esquema nuevo no se crea en bases existentes | Media | Mitigated | Borrado único documentado de la BD de desarrollo; `EnsureCreated` regenera (ADR-019 seed idempotente). |
| PII enviada al LLM externo | Alta | Mitigated | `pii_masker` obligatorio (email, teléfono, UUID, JWT, ubicación, user_id) antes de enviar contexto. |
| MCP no disponible en runtime | Media | Mitigated | Fallback elegante por cliente y nodo; tests de indisponibilidad (`40 passed`). |
| Nombre de tabla `Feedback` vs `Feedbacks` (convención EF Core) | Media | **Resolved** | Detectado en QA (smoke real); corregido `INSERT INTO Feedbacks` en `server.py` + fixture/consultas de test. |
| Acceso cruzado de BD bajo Docker Compose (named volume) | Media | Documented | Fuera de alcance; registrado en DECISIONS como mejora futura. |

## Iteración 2 — QA formal (`qa-check US-012`)

- Repo indexado (`index_repository`), branch verificada: `feature/US-012-chatbot-recommendations`.
- Builds: backend `dotnet build` 0 errores/0 warnings; frontend `npm run build` + `npm run lint` OK (solo warning preexistente `button.tsx`); chatbot pytest `40 passed`; Biblioteca-MCP pytest `12 passed`.
- Smoke test MCP contra BD real: preferencias, recomendaciones por género (solo disponibles) y `registrar_feedback` con persistencia verificada en `Feedbacks`.
- **Bug corregido en QA:** `registrar_feedback` insertaba en `Feedback` (singular); la tabla real de EF Core es `Feedbacks`. Corregido y verificado (12 passed + smoke real). Documentado en `US-012.md` → `## Validation Iterations`.
- Documentación: `US-012.md` → `## QA Result: PASS`; esta bitácora (Iteración 2).
- PR creado vía GitHub MCP `create_pull_request`; mergeable con `main`.
- Story → `Validated` vía MCP tras el PR Gate.