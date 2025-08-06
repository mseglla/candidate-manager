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

## Servicio de archivos seguro

El proyecto incluye un servicio de subida y descarga de archivos con las siguientes características:

- Almacena los archivos de forma local en un directorio restringido (`uploads`).
- Las rutas `/files` y `/files/{id}` requieren autenticación mediante un token Bearer definido por la variable de entorno `API_TOKEN` (valor por defecto `secret-token`).
- Se valida el tamaño máximo (5 MB) y la extensión permitida del archivo.
- Si está disponible `clamscan`, se analiza el archivo en busca de malware antes de aceptarlo.

### Uso

1. Aplique las migraciones y ejecute el servidor:

   ```bash
   python migrate.py
   python app.py
   ```

2. Envíe una petición `POST /files` con autenticación y un archivo multipart para subirlo. Use `GET /files/{id}` para descargarlo.

Los archivos se guardan dentro de `uploads` con permisos restringidos.

## Auditoría y monitoreo

- Guardar eventos en la base de datos o en servicios de logging centralizado (ELK, CloudWatch).
- Registrar quién hizo qué y cuándo, incluyendo IP y usuario.
- Configurar alertas y monitoreo para eventos críticos o anomalías.
