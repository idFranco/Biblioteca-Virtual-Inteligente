-- Limpieza del residuo de datos de prueba E2E en BibliotecaVirtual.db (US-020, item 4).
--
-- Elimina de forma idempotente y FK-safe al usuario de prueba
-- 'usuario.e2e@test.local' (93C1CA75-58A0-4EAA-BA95-CFB887860A50) y todos sus
-- hijos (alquileres, notificaciones, book-requests, refresh tokens, claims,
-- roles, logins, tokens y feedbacks/preferencias si existieran).
--
-- Conserva intactos los datos demo (50 libros, incluido su stock de semilla) y
-- al usuario administrador 'admin@biblioteca.local'.
--
-- Ejecución (GATE de aprobación humana previo, backups en /tmp): connect to
-- the database with PRAGMA foreign_keys=ON and run this file.
--
--   sqlite3 workflow/database/BibliotecaVirtual.db \
--     ".bail on" "PRAGMA foreign_keys=ON;" ".read cleanup_biblioteca.sql"
--
-- Idempotente: ejecutar más de una vez no tiene efecto (los DELETE simplemente
-- no afectan a filas inexistentes).

PRAGMA foreign_keys = ON;

-- 1) Hijos directos de AspNetUsers (y de Rentals en el caso de Notifications).
DELETE FROM Notifications
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM Rentals
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM BookRequests
 WHERE RequestedBy = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM RefreshTokens
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM UserPreferences
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM Feedbacks
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

-- 2) Tablas de Identity vinculadas por UserId.
DELETE FROM AspNetUserClaims
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM AspNetUserRoles
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM AspNetUserLogins
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

DELETE FROM AspNetUserTokens
 WHERE UserId = '93C1CA75-58A0-4EAA-BA95-CFB887860A50';

-- 3) Usuario de prueba (padre).
DELETE FROM AspNetUsers
 WHERE Id = '93C1CA75-58A0-4EAA-BA95-CFB887860A50'
   AND Email = 'usuario.e2e@test.local';
