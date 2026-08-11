Clasifica la intención del usuario en el contexto de una biblioteca virtual.

Categorías posibles:
- "book_query": el usuario pregunta por un libro concreto (título, autor, ISBN).
- "recommendation": el usuario pide recomendaciones de libros.
- "status": el usuario pregunta por sus alquileres o estado de lectura.
- "other": cualquier otra consulta.

Reglas:
- Si menciona un título/obra entre comillas o con artículo, o un autor, es book_query.
- Si pregunta "qué me recomiendas", "recomiéndame", "qué leer", es recommendation.
- Si pregunta "mis alquileres", "cuánto debo devolver", "mi préstamo", es status.
- Si pregunta por un libro que no existe en el catálogo, sigue siendo book_query.

Mensaje del usuario:
"""{{ message }}"""

Responde SOLO con el nombre de la categoría.
