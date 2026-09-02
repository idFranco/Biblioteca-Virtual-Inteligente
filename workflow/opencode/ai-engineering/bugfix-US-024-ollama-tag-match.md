# Iteration Log — bugfix/US-024-ollama-tag-match

## 2026-09-02 — qa-check US-024 → PASS

- **Story:** US-024 — Tolerar el sufijo de tag (`:latest`) en el match del modelo Ollama de la validación de arranque y `/health`.
- **Rama:** `feature/US-023-startup-healthcheck`.
- **Veredicto global:** PASS — los 6 escenarios de criterios de aceptación pasan.

### Criterios de aceptación
- **AC#1 `OLLAMA_MODEL` sin tag y modelo cargado con tag por defecto (`llama3.2` vs `llama3.2:latest`)** — ✅ PASS
  - `test_ollama_ok_when_model_has_tag_suffix`: `OLLAMA_MODEL=llama3.2` + `["qwen3:8b","llama3.2:latest"]` → `check_ollama()` no lanza.
  - `test_probe_health_ollama_ok_with_tag_suffix`: `probe_health()` → `{"ollama": "ok", "groq": "ok"}`.
- **AC#2 `OLLAMA_MODEL` sin tag y modelo cargado sin tag (regresión)** — ✅ PASS
  - `test_ollama_ok_when_model_match_without_tag`: `llama3.2` vs `["llama3.2"]` → no lanza.
- **AC#3 `OLLAMA_MODEL` con tag explícito y modelo cargado con ese tag (`llama3.2:13b`)** — ✅ PASS
  - `test_ollama_ok_when_explicit_tag_matches`: `llama3.2:13b` vs `["llama3.2:latest","llama3.2:13b"]` → no lanza.
- **AC#4 Tag explícito no matchea otro tag del mismo modelo** — ✅ PASS
  - `test_ollama_explicit_tag_does_not_match_other_tag`: `llama3.2:13b` vs `["llama3.2:latest"]` → `RuntimeError` (match exacto de tag).
- **AC#5 Sin tag no matchea un modelo distinto (sin falso positivo)** — ✅ PASS
  - `test_ollama_without_tag_does_not_match_other_model`: `llama3.1` vs `["llama3.2:latest"]` → `RuntimeError`.
- **AC#6 Regresión — tests del chatbot siguen verdes** — ✅ PASS
  - `python3 -m pytest tests -q` en `workflow/chatbot` → **156 passed in 2.11s, 0 failed** (150 + 6 nuevos).

### Evidencia clave / gates
| Gate | Comando | Resultado |
|---|---|---|
| Tests chatbot | `cd workflow/chatbot && python3 -m pytest tests -q` | 156 passed |
| Gate positivo (fake `llama3.2:latest`) | `OLLAMA_MODEL=llama3.2` + fakes Ollama/GROQ | `[startup-checks] OK` exit 0 |
| Gate negativo (fake `llama3.2:latest`, `OLLAMA_MODEL=llama3.1`) | `python -m app.startup_checks` | exit 1, `El modelo local Ollama no está cargado: 'llama3.1' ... (modelos disponibles: qwen3:8b, llama3.2:latest)` |
| /health con modelo con tag | `.probe_health()` | `{"ollama": "ok", "groq": "ok"}` |
| Coherencia README↔comportamiento | Sección "Validación de arranque (US-023)" | coherente |

### Documentation Gate
Cumplido — `## QA Result` documentado en `US-024.md` (reemplazado el `Pending`); README `workflow/chatbot` actualizado (match tolerante a `:tag`; tag explícito → exacto; conteo de tests → 156). Estado en `project_state.json` y frontmatter coinciden (`Validated`).

### Observaciones no bloqueantes
- El PR #24 (mergeado a main el 2026-09-01) incluyó únicamente US-023. Los cambios de US-024 (implementados y validados en el working tree) se integran en un PR propio a continuación.

### Siguiente paso
PR vía GitHub MCP → merge a `main` (US-024 ya está en `Validated` tras qa-check PASS).
