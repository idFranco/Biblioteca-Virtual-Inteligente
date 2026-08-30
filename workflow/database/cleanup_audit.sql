-- Limpieza del residuo de datos de prueba E2E en audit.db (US-020, item 4).
--
-- Elimina de forma idempotente todas las filas de auditoría generadas por las
-- corridas E2E (correlation_id con prefijo 'e2e-' o 'test-').
--
-- Ejecución (GATE de aprobación humana previo, backups en /tmp):
--   sqlite3 workflow/database/audit.db ".read cleanup_audit.sql"

DELETE FROM audit_events
 WHERE correlation_id LIKE 'e2e-%'
    OR correlation_id LIKE 'test-%';
