# candidate-manager

Minimal API para gestionar candidatos, comentarios, usuarios, archivos, evaluaciones y un historial de actividad usando el servidor HTTP incorporado de Python y SQLite.

El backend se implementa exclusivamente en Python; no se requiere Node.js.

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

Endpoints equivalentes existen para `comments`, `evaluations`, `activities` y `users`.

- `GET /users` – lista de usuarios
- `POST /users` – crear usuario
- `GET /users/{id}` – obtener usuario
- `PUT /users/{id}` – actualizar usuario
- `DELETE /users/{id}` – eliminar usuario

Los endpoints de `files` siguen disponibles y requieren autenticación.

### Documentación
La documentación OpenAPI está disponible en [`/swagger.json`](http://localhost:8000/swagger.json).

## Servicio de archivos seguro

El proyecto incluye un servicio de subida y descarga de archivos con las siguientes características:

- Almacena los archivos de forma local en un directorio restringido (`uploads`).
- Las rutas `/files` y `/files/{id}` requieren autenticación mediante un token Bearer definido por la variable de entorno `API_TOKEN` (valor por defecto `secret-token`).
- Se valida el tamaño máximo (5 MB) y la extensión permitida del archivo.
- Si está disponible `clamscan`, se analiza el archivo en busca de malware antes de aceptarlo.
- El servidor procesa formularios `multipart/form-data` sin depender de `cgi`, utilizando `email.parser` y `urllib.parse`.

### Uso

1. Aplique las migraciones y ejecute el servidor:

   ```bash
   python migrate.py
   python app.py
   ```

2. Envíe una petición `POST /files` con autenticación y un archivo multipart para subirlo. Use `GET /files/{id}` para descargarlo.

Los archivos se guardan dentro de `uploads` con permisos restringidos.

## Frontend ligero

En el directorio `frontend/` se incluye una interfaz web sencilla para gestionar usuarios.
Los archivos son estáticos (`index.html`, `app.js` y `style.css`) y consumen la API directamente.

Para probarla, sirve el directorio con cualquier servidor estático, por ejemplo:

```bash
python -m http.server --directory frontend 3000
```

Con la API ejecutándose en `http://localhost:8000`, abre `http://localhost:3000` en el navegador.
