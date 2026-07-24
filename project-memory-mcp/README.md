# Project Memory MCP Server

Este es un servidor local basado en el **Model Context Protocol (MCP)** desarrollado en Node.js. Su objetivo principal es actuar como la "fuente de la verdad" del ciclo de vida del proyecto, gestionando el estado y la persistencia de las Historias de Usuario.

## Propósito

En la arquitectura de desarrollo evolutivo con IA, los agentes no pueden depender de su memoria a corto plazo para recordar qué están construyendo. Este servidor reemplaza los archivos de texto estáticos tradicionales por una API local estructurada. 

Garantiza que la regla de oro **"Plan-Before-Build"** se cumpla, impidiendo que los agentes escriban código si una historia no ha pasado por las fases correspondientes de aprobación.

## Stack Tecnológico
* Node.js
* `@modelcontextprotocol/sdk`

## Herramientas Expuestas (Tools)

Este servidor expone las siguientes herramientas al entorno de OpenCode:

| Herramienta | Descripción | Agente Principal |
| :--- | :--- | :--- |
| `project_memory_create_story` | Crea un archivo físico `.md` para la historia de usuario en `workflow/opencode/user-stories/` utilizando `.opencode/user-stories/TEMPLATE.md` como base, e inicializando el estado en `Draft`. | Technical Lead |
| `project_memory_get_context` | Lee el estado actual desde la base de datos JSON. Actúa como mecanismo de bloqueo para saber si una historia está aprobada o rechazada para implementarse. | Todos los agentes |
| `project_memory_advance_status` | Transiciona una historia validando su ciclo de vida (`Draft` ➔ `Planned` ➔ `Approved` ➔ `In Progress` ➔ `Implemented` ➔ `Validated` o `Rejected`). | Technical Lead / QA |

## Integración con OpenCode

No es necesario iniciar este servidor manualmente. Está configurado en el archivo maestro `opencode.json` para ejecutarse automáticamente en un proceso en segundo plano bajo demanda cuando un agente necesita consultar la memoria del proyecto.

**Configuración en `opencode.json`:**
```json
"mcp": {
  "project-lifecycle": {
    "type": "local",
    "command": ["node", "project-memory-mcp/server.js"],
    "enabled": true
  }
}
```

## Estructura de Datos y Persistencia

El servidor mantiene una doble fuente de persistencia estrictamente sincronizada:

1. **Base de Datos Local (`project_state.json`):** Mantiene el estado en memoria para consultas ultrarrápidas y validación de reglas de transición.
2. **Archivos Físicos (`workflow/opencode/user-stories/*.md`):** Archivos legibles por humanos donde se actualiza dinámicamente el estado mediante YAML/Frontmatter.
3. **Logs (`project-lifecycle.log`):** Registro de errores internos y fallos de sistema de archivos sin romper la comunicación JSON-RPC del protocolo MCP.

## Relación con Codebase Memory MCP

Es importante distinguir este servidor de la herramienta `codebase-memory`. Ambos trabajan en conjunto, pero tienen responsabilidades estrictamente separadas:

* **Project Memory MCP (Este servidor):** Gestiona exclusivamente la **memoria del proceso**. Sabe qué se debe hacer (Historias de Usuario), el estado de aprobación y las reglas de negocio.

* **Codebase Memory MCP:** Gestiona la **memoria técnica**. Indexa el código fuente, mapea el grafo de dependencias de la arquitectura y permite a los agentes buscar implementaciones específicas dentro de los archivos físicos.

Durante el flujo de trabajo (`qa-check` o `plan-user-story`), los agentes consultarán *este* servidor para obtener autorización, y luego utilizarán *codebase-memory* para leer la estructura del código antes de actuar.

## Resiliencia y Mecanismos de Seguridad

Para garantizar la integridad del ciclo de vida en entornos de IA, este servidor implementa programación defensiva:
* **Escritura Atómica:** El archivo `project_state.json` se actualiza mediante archivos `.tmp` y `fs.renameSync` para evitar corrupciones si el proceso colapsa durante una escritura.
* **Prevención de Estados Huérfanos:** El servidor obliga a actualizar el archivo físico `.md` *antes* de confirmar el cambio en el JSON. Si el sistema de archivos falla, la transacción lógica se aborta.
* **Normalización Cross-Platform:** Todo el procesamiento de texto normaliza silenciosamente los saltos de línea (`\r\n` a `\n`) para evitar fallos de expresiones regulares si la plantilla se edita desde Windows.
* **Inyección Segura:** Las variables dinámicas en el Markdown se inyectan utilizando *callbacks* literales, evitando que caracteres especiales (como `$`) corrompan la generación de la historia.

### Limitaciones Conocidas (Technical Debt)
* **Concurrencia Estricta:** El ciclo de lectura y mutación del JSON asume un entorno donde las herramientas se invocan secuencialmente. En caso de desplegar un enjambre multi-agente (*swarm*) altamente concurrente en el futuro, el estado deberá migrarse a SQLite para aprovechar bloqueos transaccionales (WAL).
