import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url';
import crypto from "crypto";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Las rutas siempre se resolverán hacia arriba desde la carpeta 'project-memory-mcp'
const ROOT_DIR = path.resolve(__dirname, "..");

const DB_FILE = path.join(__dirname, "project_state.json");
const LOG_FILE = path.join(__dirname, "project-lifecycle.log");

// Carpeta donde se generan/actualizan las historias reales
const STORIES_DIR = path.join(ROOT_DIR, "workflow", "opencode", "user-stories");

// Plantilla base, en su ubicación real (separada de STORIES_DIR)
const TEMPLATE_PATH = path.join(ROOT_DIR, ".opencode", "user-stories", "TEMPLATE.md");

// Función para escritura atómica de JSON, previene corrupción por escrituras interrumpidas
function atomicWriteJsonSync(filePath, data) {
    const tempPath = `${filePath}.${crypto.randomBytes(4).toString('hex')}.tmp`;
    try {
        fs.writeFileSync(tempPath, JSON.stringify(data, null, 2), "utf-8");
        fs.renameSync(tempPath, filePath);
    } catch (error) {
        if (fs.existsSync(tempPath)) {
            try { fs.unlinkSync(tempPath); } catch (e) { /* Ignorar error de limpieza */ }
        }
        throw error;
    }
}

// Función segura para registrar errores sin romper MCP
function logError(contextMessage, error) {
    const timestamp = new Date().toISOString();
    const errorDetails = error instanceof Error ? error.stack : JSON.stringify(error);
    const logEntry = `[${timestamp}] ERROR: ${contextMessage}\n${errorDetails}\n\n`;
    
    // 1. Escribir en el archivo físico
    fs.appendFileSync(LOG_FILE, logEntry, "utf-8");
    
    // 2. Redirigir a stderr para que OpenCode lo capture en sus logs de depuración
    console.error(logEntry);
}

// Inicializar base de datos
if (!fs.existsSync(DB_FILE)) {
    fs.mkdirSync(path.dirname(DB_FILE), { recursive: true });
    fs.writeFileSync(DB_FILE, JSON.stringify({ stories: {}, modules: {} }, null, 2));
}

// Inicializar directorio de historias físicas
if (!fs.existsSync(STORIES_DIR)) {
    fs.mkdirSync(STORIES_DIR, { recursive: true });
}

const server = new Server(
    { name: "project-lifecycle-memory", version: "1.0.0" },
    { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        {
            name: "project_memory_get_context",
            description: "Devuelve el estado actual de control de flujos e historias del proyecto.",
            inputSchema: {
                type: "object",
                properties: {}
            }
        },
        {
            name: "project_memory_create_story",
            description: "Registra una nueva Historia de Usuario en estado 'Draft' y crea su archivo físico.",
            inputSchema: {
                type: "object",
                properties: {
                    story_id: { type: "string", description: "ID único, ej: US-001" },
                    title: { type: "string", description: "Título de la historia" },
                    description: { type: "string", description: "En formato Como/Quiero/Para" }
                },
                required: ["story_id", "title", "description"]
            }
        },
        {
            name: "project_memory_advance_status",
            description: "Avanza secuencialmente el estado de una historia validando el ciclo y actualiza el archivo físico.",
            inputSchema: {
                type: "object",
                properties: {
                    story_id: { type: "string" },
                    next_status: { type: "string", enum: ["Planned", "Approved", "In Progress", "Implemented", "Validated", "Rejected"] }
                },
                required: ["story_id", "next_status"]
            }
        }
    ]
}));

function updateMarkdownFile(storyId, title, description, status) {
    const filePath = path.join(STORIES_DIR, `${storyId}.md`);
    
    try {
        if (fs.existsSync(filePath)) {
            // Si el archivo ya existe, actualizar solo el estado
            let content = fs.readFileSync(filePath, "utf-8");
            
            // Normalizar saltos de línea por seguridad en lecturas posteriores
            content = content.replace(/\r\n/g, "\n");
            
            // Usar función de reemplazo () => para evitar que '$' corrompa el texto
            const updatedContent = content.replace(/^status:\s*.*$/m, () => `status: ${status}`);
            fs.writeFileSync(filePath, updatedContent, "utf-8");
        } else {
            // Si no existe, validar que la plantilla base exista en la ruta correcta
            if (!fs.existsSync(TEMPLATE_PATH)) {
                throw new Error(`CRÍTICO: No se encontró el archivo base TEMPLATE.md en ${TEMPLATE_PATH}`);
            }

            // Leer la plantilla física
            let templateContent = fs.readFileSync(TEMPLATE_PATH, "utf-8");

            // NORMALIZACIÓN CROSS-PLATFORM: Convertir CRLF (Windows) a LF (Unix)
            templateContent = templateContent.replace(/\r\n/g, "\n");

            // Reemplazos literales seguros utilizando () => variable
            templateContent = templateContent.replace(/US-XXX/g, () => storyId);
            templateContent = templateContent.replace(/<Título>/g, () => title);
            templateContent = templateContent.replace(/^status:\s*.*$/m, () => `status: ${status}`);
            
            // Reemplazar la sección de User Story genérica (As a...) por la descripción real
            const userStoryPlaceholder = /As a <role>,\nI want <capability>,\nso that <benefit>\./;
            templateContent = templateContent.replace(userStoryPlaceholder, () => description);

            // Escribir el nuevo archivo generado en workflow/opencode/user-stories/
            fs.writeFileSync(filePath, templateContent, "utf-8");
        }
    } catch (error) {
        logError(`Fallo al intentar actualizar o crear el archivo físico Markdown de la historia ${storyId}`, error);
        throw error; 
    }
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
        const { name, arguments: args } = request.params;

        if (name === "project_memory_get_context") {
            const db = JSON.parse(fs.readFileSync(DB_FILE, "utf-8"));
            return { content: [{ type: "text", text: JSON.stringify(db, null, 2) }] };
        }

        if (name === "project_memory_create_story") {
            const db = JSON.parse(fs.readFileSync(DB_FILE, "utf-8"));
        
            if (db.stories[args.story_id]) {
                return { content: [{ type: "text", text: `Error: La historia ${args.story_id} ya existe.` }] };
            }
        
            updateMarkdownFile(args.story_id, args.title, args.description, "Draft");
            db.stories[args.story_id] = { title: args.title, description: args.description, status: "Draft" };
            atomicWriteJsonSync(DB_FILE, db);
        
            return { content: [{ type: "text", text: `Éxito: ${args.story_id} creada en estado 'Draft'. El archivo físico fue generado.` }] };
        }

        if (name === "project_memory_advance_status") {
            const db = JSON.parse(fs.readFileSync(DB_FILE, "utf-8"));
            
            const story = db.stories[args.story_id];
            if (!story) return { content: [{ type: "text", text: `Error: La historia ${args.story_id} no existe.` }] };

            const flow = { 
                "Draft": "Planned", 
                "Planned": "Approved", 
                "Approved": "In Progress", 
                "In Progress": "Implemented", 
                "Implemented": "Validated",
                "Rejected": "In Progress"
            };
            
            const isValidTransition = 
                (flow[story.status] === args.next_status) || 
                (story.status === "Implemented" && args.next_status === "Rejected");

            if (!isValidTransition) {
                return { content: [{ type: "text", text: `Rechazado: Transición no válida de '${story.status}' a '${args.next_status}'.` }] };
            }

            updateMarkdownFile(args.story_id, story.title, story.description, args.next_status);
            story.status = args.next_status;
            atomicWriteJsonSync(DB_FILE, db);

            return { content: [{ type: "text", text: `Éxito: Estado de ${args.story_id} actualizado a '${args.next_status}'.` }] };
        }
        
        throw new Error(`Herramienta no reconocida por el servidor: ${name}`);
        
    } catch (error) {
        // BUG-03 FIX: logError envuelto en try-catch secundario para evitar
        // que un fallo de escritura en el log file crashee el proceso MCP.
        try {
            logError(`Fallo crítico ejecutando la herramienta ${request.params?.name}`, error);
        } catch (logErr) {
            console.error(`[${new Date().toISOString()}] FATAL: logError también falló. Error original: ${error?.message}. Error de log: ${logErr?.message}`);
        }
        
        return { 
            content: [{ 
                type: "text", 
                text: `Error interno del servidor MCP: No se pudo ejecutar la acción. Revisa el archivo project-lifecycle.log para más detalles.` 
            }],
            isError: true 
        };
    }
});

const transport = new StdioServerTransport();
await server.connect(transport);
