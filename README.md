# candidate-manager

Minimal API para gestionar candidatos, comentarios, usuarios, archivos, evaluaciones y un historial de actividad usando el servidor HTTP incorporado de Python y SQLite.

## Uso

Antes de iniciar el servidor es necesario aplicar las migraciones de base de datos.

```bash
python migrate.py
python app.py
```

El servidor se ejecutará en `http://localhost:8000`.

### Endpoints principales
- `GET /candidates` – lista de candidatos
- `POST /candidates` – crear candidato
- `GET /candidates/{id}` – obtener candidato
- `PUT /candidates/{id}` – actualizar candidato
- `DELETE /candidates/{id}` – eliminar candidato

Recursos análogos existen para `comments`, `evaluations` y `activities`. Además se han añadido tablas `users` y `files` disponibles mediante los servicios internos.

### Documentación
La documentación OpenAPI está disponible en [`/swagger.json`](http://localhost:8000/swagger.json).
