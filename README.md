# candidate-manager

Example FastAPI service demonstrating secure file upload and download.

## Features

- Stores files locally in a restricted directory.
- Upload and download routes require a bearer token.
- Validates file type and size (max 5 MB).
- Attempts malware scanning via `clamscan` if available.

## Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:

   ```bash
   uvicorn main:app --reload
   ```

3. Interact with the API using the token defined by `API_TOKEN` (default `secret-token`).
