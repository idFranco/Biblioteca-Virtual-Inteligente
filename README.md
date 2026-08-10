Trabajo Práctico Integrador — Sistema Web Fullstack con AI Engineering, MCP y Chatbot basado en Grafo.

---

## 1. Descripción general

**Biblioteca Virtual Inteligente** es una aplicación web fullstack diseñada para gestionar una biblioteca virtual. Permite administrar usuarios, roles, catálogo de libros, alquileres y notificaciones de vencimiento.

Como diferencial, integra un **chatbot inteligente** desarrollado con **LangChain + LangGraph**, apoyándose en el protocolo **MCP (Model Context Protocol)** para aislar la lógica de negocio y auditar la seguridad.

### Alcance Funcional (10 Casos de Uso Core)
1. Registro de cuenta (Público)
2. Inicio de sesión (JWT)
3. Gestión de roles y permisos (Admin)
4. Interfaz condicionada por roles y permisos (UX)
5. Búsqueda y filtrado de libros en catálogo
6. CRUD completo de libros (Admin/Bibliotecario)
7. Alquiler de libros con fecha límite de devolución
8. Generación automática de notificaciones de vencimiento próximo
9. Registro de devoluciones y liberación de stock
10. Chatbot inteligente con memoria persistente y grafo conversacional

---

## 2. Arquitectura Base

```mermaid
flowchart TD
    U[Usuario] --> FE[Frontend React]
    FE -->|HTTP + JWT| BE[Backend .NET 9]
    BE --> DB[(SQLite)]
    
    FE -->|HTTP Request| AUDIT_IN[Security-Audit-MCP: Input Audit]
    AUDIT_IN --> CHAT[Chatbot API FastAPI]
    CHAT --> GRAPH[LangGraph + LangChain]
    GRAPH --> BMCP[Biblioteca-MCP]
    GRAPH --> OMCP[Open Library MCP]
    BMCP --> DB
    CHAT --> AUDIT_OUT[Security-Audit-MCP: Output Sanitization]
    AUDIT_OUT -->|HTTP Response| FE
```
    
---

## 3. Desarrollo Evolutivo (AI Engineering)

Este proyecto se desarrolla de forma incremental mediante flujos automatizados de agentes de IA (OpenCode). No se escribe código de forma descontrolada, todo pasa por un estricto pipeline de aprobación.

### Ciclo de Vida de las Historias de Usuario
Cada nueva funcionalidad o requerimiento sigue de manera obligatoria esta secuencia orquestada mediante comandos específicos en el modo **Build**:

1. **Requerimiento (`create-user-story`)** El usuario ingresa una necesidad en lenguaje natural anteponiendo el comando.
2. **Historia de Usuario** El *Technical Lead* crea el archivo físico de la historia (`US-XXX`). El *Functional Analyst* redacta los criterios de aceptación y reglas de negocio.
3. **Planificación por roles (`plan-user-story`)** El *Architect* y los *Developers* trazan el plan técnico colaborativo sin tocar código.
4. **Actualización a 'Planned'** El sistema de control (MCP) registra la historia como planificada.
5. **Pregunta de Aprobación ➔** Compuerta de seguridad: el agente se detiene y pide autorización explícita para programar.
6. **Implementación incremental (`implement-user-story`)** Una vez aprobada explícitamente, los desarrolladores escriben el código exacto de ese incremento.
7. **Validación QA (`qa-check`) ➔** El agente de *QA* audita el código contra los criterios de aceptación y prueba el flujo.
8. **Actualización a 'Validated' ➔** Si pasa con éxito, se crea un *Pull Request* automático en GitHub y el estado se cierra.

```mermaid
gantt
    title Ciclo de Vida Inmutable de una Historia de Usuario (Gate-to-Gate)
    dateFormat  X
    axisFormat %s
    
    section 1. REQUERIMIENTO
    Crear Historia (Draft) :active, st1, 0, 10
    
    section 2. PLANIFICACIÓN
    Diseño & Plan de Roles :crit, st2, 10, 30
    Apertura Rama Git (Kebab-case) :st3, 20, 30
    Compuerta de Aprobación Usuario :milestone, st4, 30, 0
    
    section 3. IMPLEMENTACIÓN
    Código Incremental (In Progress) :st5, 30, 60
    Push automático a GitHub :st6, 55, 60
    
    section 4. CALIDAD (QA)
    Indexación Codebase & Testeo :crit, st7, 60, 80
    Apertura Automática de PR :st8, 75, 80
    Cierre e Integración (Validated) :milestone, st9, 80, 0
```

### Guía de Comandos y Estados del Pipeline (Flujo Inmutable)

El desarrollo está completamente automatizado y gobernado por el servidor de ciclo de vida. Cada funcionalidad debe atravesar de forma obligatoria las siguientes transiciones de estado mediante comandos secuenciales en la terminal:

| Fase | Comando Ejecutado | Rol Líder | Estado en MCP | Compuerta de Seguridad / Restricciones Estrictas |
| :--- | :--- | :--- | :--- | :--- |
| **1. Entrada** | `create-user-story "Como... Quiero... Para..."` | Technical Lead | `Draft` | El sistema valida la sintaxis y genera un ID único incremental (ej. `US-001`). |
| **2. Plan** | `plan-user-story "US-XXX"` | Technical Lead | `Planned` | **Prohibido modificar código.** Coordina el diseño entre analistas y arquitectos. Exige definir de forma interactiva la rama Git (`tipo/US-XXX-descripcion`). |
| **3. Aprobación** | `approve-user-story "US-XXX"` | Technical Lead | `Approved` | Avanza explícitamente la historia autorizando el comienzo de la programación. |
| **4. Build** | `implement-user-story "US-XXX"` | Technical Lead | `In Progress` $\rightarrow$ `Implemented` | Bloqueado si el estado no es `Approved` o `Rejected`. El agente escribe el incremento de código exacto y realiza un *push* directo y automatizado a la rama de la funcionalidad en GitHub. |
| **5. QA** | `qa-check "US-XXX"` | QA | `Validated` o  `Rejected` | Ejecuta `index_repository` para analizar los cambios. Valida criterios de aceptación y documenta en el `.md`. Si pasa con éxito, abre un **Pull Request** automático hacia la rama main. Si falla, devuelve a `Rejected` y se detiene. |

**Nota de Cumplimiento** Cualquier intento de saltarse una fase, modificar código fuera de la fase *Build*, o utilizar nombres de ramas sin el formato reglamentario provocará el rechazo automático del comando por parte de los agentes.

**Nota sobre la documentación técnica**
La documentación detallada, endpoints y configuraciones de cada componente no están centralizadas aquí. El rol de **Technical Writer** creará y actualizará automáticamente los archivos `README.md` dentro de cada módulo (`/backend`, `/frontend`, `/chatbot`, `/mcp`) **a medida que el código atraviese este ciclo y sea validado**.

---

## 4. Stack Tecnológico General

- Frontend: React, TypeScript, Tailwind CSS.
- Backend: C#, .NET 9, ASP.NET Core Web API, EF Core, SQLite.
- IA & Chatbot: Python, FastAPI, LangChain, LangGraph.
- Orquestación: Model Context Protocol (MCP), Docker Compose.


---

## 5. Project Structure

```
├── docker-compose.yml              # Docker Compose for all services
├── .env.example                   # Plantilla de variables de entorno (copiar a .env)
├── workflow/
│   ├── backend/                     # .NET 9 Clean Architecture
│   │   ├── BibliotecaVirtual.slnx
│   │   ├── .dockerignore
│   │   └── src/
│   │       ├── BibliotecaVirtual.Domain/       # Entities, Enums, ValueObjects, Interfaces
│   │       ├── BibliotecaVirtual.Application/  # CQRS, Commands, Queries, Validators
│   │       ├── BibliotecaVirtual.Infrastructure/ # EF Core DbContext, Services
│   │       └── BibliotecaVirtual.Api/          # Controllers, Middleware, Program.cs
│   ├── frontend/                    # React 18 + TypeScript + Vite
│   │   ├── Dockerfile
│   │   ├── nginx.conf              # Nginx server: SPA fallback + cache de assets
│   │   ├── .dockerignore
│   │   └── src/
│   │   │   ├── routes/             # Route components
│   │   │   ├── components/         # UI components
│   │   │   ├── services/           # API client services
│   │   │   ├── types/              # TypeScript type definitions
│   │   │   └── lib/                # Utility functions
│   │   └── ...
│   ├── chatbot/                     # FastAPI + LangChain + LangGraph
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── graph/              # LangGraph nodes
│   │       ├── prompts/            # Prompt templates
│   │       ├── mcp_clients/        # MCP client wrappers
│   │       └── services/           # Business services
│   ├── mcp/
│   │   ├── biblioteca-mcp/         # Domain MCP server
│   │   └── security-audit-mcp/     # Security MCP server
│   ├── database/                    # SQLite database files
│   └── opencode/                    # User stories, AI engineering logs
```

---

## 6. Prerrequisitos y Configuración del Entorno

### 6.1 Configuración de Variables de Entorno (.env)

Para que el flujo de automatización y los servidores MCP funcionen correctamente, debes crear un archivo `.env` en la raíz de tu proyecto (o configurar las variables en tu entorno) con los siguientes valores obligatorios:

```env
# Personal Access Token (Classic) de GitHub con permisos de repositorio (Necesario para que el comando qa-check abra Pull Requests automáticamente)
GITHUB_TOKEN=ghp_tu_token_aqui

# Ruta a la base de datos SQLite (Necesario para que los MCP de Python interactúen con la DB del backend)
# Define la ruta proyectada, el backend creará el archivo automáticamente en su primer build.
DATABASE_PATH=./workflow/database/BibliotecaVirtual.db

# Clave simétrica de firma JWT del backend (Obligatoria para levantar el stack con Docker Compose)
# Generar con: openssl rand -base64 48
JWT_KEY=

# Cuenta administradora inicial que se siembra en el primer arranque del backend
ADMIN_EMAIL=admin@biblioteca.local
ADMIN_PASSWORD=
```

Plantilla completa con valores de ejemplo: ver `.env.example` en la raíz del repositorio.

### 6.2 Codebase Memory MCP
Para que los agentes de IA puedan explorar la arquitectura del proyecto de forma autónoma, este repositorio depende de Codebase Memory MCP, el cual debe estar instalado a nivel global en tu sistema.

Dependiendo de tu sistema operativo, asegúrate de tener Node.js instalado y ejecuta el siguiente comando en tu terminal:

Linux & macOS:

**Linux & macOS:**
```bash
sudo npm install -g codebase-memory-mcp
```

**Windows (Ejecutar CMD o PowerShell como Administrador):**
```bash
npm install -g codebase-memory-mcp
```

Nota: El archivo opencode.json de este proyecto asume que el comando `codebase-memory-mcp` está disponible globalmente en tu variable de entorno PATH.

#### Versión con UI

```bash
codebase-memory-mcp --ui=true --port=9749
```
Luego abre en el navegador:
```bash
http://localhost:9749
```

### 6.3 Configuración Local para Desarrollo

#### Backend (.NET 9)

```bash
# Navegar al directorio del backend
cd workflow/backend

# Restaurar paquetes NuGet
dotnet restore

# Compilar la solución
dotnet build

# Ejecutar la API (Swagger en /swagger)
dotnet run --project src/BibliotecaVirtual.Api
```

La API estará disponible en `https://localhost:5001/swagger`. La base de datos SQLite se crea automáticamente en `workflow/database/`.

**Variables de entorno del backend:**

- `AUTH_RATE_LIMIT_PER_MINUTE` (default `10`): límite de la policy `auth` del rate limiter (register/login/refresh/revoke) por ventana de 1 minuto. Eleva el valor para baterías de pruebas que disparen ráfagas sin falsos `429`.
- `SQLitePCLRaw.lib.e_sqlite3` está pinnado a `2.1.12` para mitigar `NU1903` (GHSA-2m69-gcr7-jv3q). Las versiones parcheadas actuales requieren glibc ≥ 2.34; si tu host usa glibc antiguo (p. ej. Debian 11, glibc 2.31), ejecuta el backend vía Docker (`docker compose up --build backend`) — la imagen `dotnet/aspnet:10.0` incluye glibc compatible.

#### Frontend (React + TypeScript + Vite)

```bash
# Navegar al directorio del frontend
cd workflow/frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:5173`.

---

### 6.5 Instalación de Dependencias MCP (Local)
Aunque la aplicación final se ejecuta en Docker, la orquestación de IA y los servidores MCP que interactúan con tu código deben correr directamente en tu máquina anfitriona. Antes de iniciar cualquier flujo, instala las dependencias necesarias:

**1. Servidor de Ciclo de Vida (Node.js)**
Responsable de gestionar el estado de las Historias de Usuario.
```bash
cd project-memory-mcp
npm install
cd ../..
```

**2. Servidores de Dominio y Seguridad (Python)**

Responsables de auditar la seguridad (`Security-Audit-MCP`) y conectar el chatbot con la base de datos (`Biblioteca-MCP`). Asegúrate de tener Python 3.10+ instalado.

## Crear entorno virtual en la raíz (opcional pero recomendado)
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

## Instalar dependencias para los servidores MCP de Python
```bash
pip install mcp fastmcp
```

---

## 7. Ejecución local rápida (Docker)

El proyecto está preparado para levantarse por completo mediante contenedores para la aplicación (Frontend, Backend, Chatbot):

**1. Crear el archivo `.env` a partir de la plantilla:**

```bash
cp .env.example .env
# Completar JWT_KEY (openssl rand -base64 48) y ADMIN_PASSWORD (>= 8 chars, 1 mayúscula, 1 dígito)
```

> El backend requiere `JWT_KEY`, `ADMIN_EMAIL` y `ADMIN_PASSWORD` para arrancar (fail-fast). Sin `.env`, el comando de compose aborta con un mensaje claro.

**2. Levantar el stack:**

```bash
docker compose up --build
```

| Servicio | URL | Puerto contenedor | Puerto host |
|---|---|---|---|
| Frontend (Nginx + SPA) | http://localhost:5173 | 5173 | 5173 |
| Backend API (.NET 9) | http://localhost:5000 | 5000 | 5000 |
| Chatbot API (FastAPI) | http://localhost:8000 | 8000 | 8000 |
| SQLite | — | volumen `database_data` en `/app/database` | — |

Notas:
- El contenedor del frontend sirve la SPA con fallback para rutas de React Router (refrescar `/login` no devuelve 404) y embebe la URL base de la API `http://localhost:5000` en el bundle (build arg `VITE_API_BASE_URL`).
- En el primer arranque el backend siembra roles/permisos y el usuario administrador definido por `ADMIN_EMAIL`/`ADMIN_PASSWORD`; el JWT se firma con `JWT_KEY`.
- La base SQLite persiste en el volumen Docker `database_data` (`./workflow/database/` solo para desarrollo local, fuera de contenedores).
- Para detener: `docker compose down` (añade `-v` si quieres eliminar también el volumen de datos).
