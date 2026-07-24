# OpenCode Control Plane - AI Engineering Architecture

Este directorio (`.opencode/`) constituye el núcleo de gobernanza, memoria y control operativo para los agentes autónomos del proyecto **Biblioteca Virtual Inteligente**.

No es simple documentación; es el **motor de estados y reglas** que garantiza que el LLM opere de manera determinista, segura y estructurada, evitando alucinaciones, bucles infinitos y modificaciones de código no autorizadas.

---

## Estructura de Directorios

### 1. `/commands` (Standard Operating Procedures - SOPs)
Contiene los manuales de ejecución paso a paso (SOPs) que los agentes deben seguir ciegamente al ejecutar comandos de ciclo de vida.
*   **Propósito:** Transformar instrucciones complejas en algoritmos secuenciales a prueba de fallos.
*   **Archivos clave:** `create-user-story.md`, `plan-user-story.md`, `implement-user-story.md`, `qa-check.md`, `read-graph.md`, `approve-user-story.md`.
*   **Mecánica:** El archivo `opencode.json` apunta a estos archivos, obligando al agente a leer el protocolo exacto antes de interactuar con Git, MCPs o el sistema de archivos.

### 2. `/instructions` (Hard Constraints & Dynamic Routing)
Contiene las reglas absolutas de arquitectura, restricciones tecnológicas y directivas de comportamiento.
*   **Propósito:** Imponer límites (guardrails) según el contexto del trabajo a realizar.
*   **Archivos clave:**
    *   `READ-GRAPH-FIRST.md`: La barrera principal que obliga al agente a verificar el estado en la base de datos de historias de usuario antes de actuar.
    *   `git-rules.md`: Control estricto de ramas, prohibición de comandos destructivos y uso obligatorio del MCP de GitHub.
    *   `backend-rules.md`, `frontend-rules.md`, `chatbot-rules.md`: Reglas Clean Architecture, prohibición de lógica en controladores, uso de LangGraph, etc.

### 3. `/memory` (Architectural Context)
El registro histórico inmutable de las decisiones del proyecto.
*   **Propósito:** Prevenir la "amnesia del agente" entre sesiones y evitar que sugiera tecnologías que violen el stack establecido.
*   **Archivos clave:** 
    *   `DECISIONS.md`: Registro de Architecture Decision Records (ADRs) como el uso de SQLite, JWT, LangGraph y la topología de los MCPs.

### 4. `/roles` (Agent Personas)
Define los perfiles que el LLM debe adoptar según la tarea requerida.
*   **Propósito:** Segmentar las responsabilidades para evitar que un solo prompt intente abarcar demasiado contexto.
*   **Roles definidos:** `architect`, `ai-engineer`, `backend-developer`, `frontend-developer`, `functional-analyst`, `qa`, `technical-lead`, `technical-writer`.
*   **Regla de oro:** Todos los roles comparten la restricción **"Planning First Rule"**; no pueden escribir código si la historia de usuario no está explícitamente en estado *Approved*.

### 5. `/skills` (Checklists de Ejecución)
Define el conocimiento técnico granular y los pasos de validación específicos para cada tecnología.
*   **Propósito:** Estandarizar la forma en que los agentes escriben y validan código.
*   **Skills definidos:** `auth-permissions`, `documentation`, `dotnet-clean-architecture`, `langgraph-chatbot`, `mcp-security-audit`, `mcp-tools`, `react-permissions`, `testing-qa`.
*   **Uso:** El agente carga la habilidad correspondiente en su memoria de corto plazo para ejecutar tareas de implementación o QA.

### 6. `/user-stories` (State Machine & Requirements)
La base de datos estática de los requerimientos del proyecto.
*   **Propósito:** Funcionar como el "backend" del `project-memory-mcp`.
*   **Archivos clave:**
    *   `TEMPLATE.md`: La plantilla base con la estructura obligatoria de toda historia (Descripción, Casos de Uso impactados, Plan Técnico, Resultado de QA).
    *   *(Nota: Las historias físicas generadas dinámicamente residen en `workflow/opencode/user-stories/` para mantener limpio el entorno de configuración)*.

---

## Mecanismos de Seguridad Activos

1.  **PR Gate:** Ninguna historia puede ser validada sin que la herramienta `create_pull_request` del MCP de GitHub se ejecute exitosamente.
2.  **Implementation Gate:** Los agentes tienen prohibido modificar archivos de la aplicación si el estado devuelto por el MCP no es explícitamente `Approved` o `Rejected`.
3.  **Circuit Breaker:** Ante errores de compilación (`dotnet build` o `npm run build`), el agente se detiene forzosamente después de 3 intentos fallidos para evitar bucles infinitos.
4.  **Zero-Prompt-Injection:** Los inputs y outputs de IA generados por el proyecto son filtrados por el `Security-Audit-MCP`.
