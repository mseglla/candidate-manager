# candidate-manager

Minimal API para gestionar candidatos, comentarios, evaluaciones y actividades usando el servidor HTTP incorporado de Python y SQLite.

## Uso

```bash
python app.py
```

El servidor se ejecutará en `http://localhost:8000`.

### Endpoints principales
- `GET /candidates` – lista de candidatos
- `POST /candidates` – crear candidato
- `GET /candidates/{id}` – obtener candidato
- `PUT /candidates/{id}` – actualizar candidato
- `DELETE /candidates/{id}` – eliminar candidato

Recursos análogos existen para `comments`, `evaluations` y `activities`.

### Documentación
La documentación OpenAPI está disponible en [`/swagger.json`](http://localhost:8000/swagger.json).
