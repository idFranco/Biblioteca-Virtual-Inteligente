# SOP: create-user-story

**Modo planificación.** A partir del requerimiento proporcionado en `$ARGUMENTS`, ejecuta ESTRICTAMENTE las siguientes acciones en orden:

1. **CREACIÓN:** Invoca la herramienta `project_memory_create_story` pasándole un `story_id` incremental (ej: US-001, US-002), título y descripción en formato Como/Quiero/Para.
2. **DETENTE:** Tienes ESTRICTAMENTE PROHIBIDO hacer preguntas al usuario, adivinar intenciones, avanzar de fase automáticamente o ejecutar herramientas adicionales.
3. **CIERRE Y GUÍA DINÁMICA:** Informa al usuario que la historia fue registrada exitosamente en estado 'Draft' y cierra tu respuesta emitiendo EXACTAMENTE este bloque sin modificaciones (reemplazando `US-XXX` por el ID real recién generado): "The story US-XXX has been created in Draft status. To authorize the planning phase, you MUST execute the following command in your terminal: plan-user-story US-XXX"
