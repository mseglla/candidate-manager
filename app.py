import json
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import cgi

import db
import services

API_TOKEN = os.getenv("API_TOKEN", "secret-token")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTS = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.chmod(UPLOAD_DIR, 0o700)


def is_authenticated(handler):
    auth = handler.headers.get("Authorization", "")
    return auth == f"Bearer {API_TOKEN}"


def send_file(handler, path, filename):
    try:
        with open(path, "rb") as f:
            data = f.read()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/octet-stream")
        handler.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
        handler.end_headers()
        handler.wfile.write(data)
    except FileNotFoundError:
        send_json(handler, {"error": "Not found"}, 404)


def parse_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    if length:
        data = handler.rfile.read(length)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
    return {}


def send_json(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/swagger.json':
            try:
                with open('swagger.json', 'r') as f:
                    spec = json.load(f)
                send_json(self, spec)
            except FileNotFoundError:
                send_json(self, {'error': 'Documentation not found'}, 404)
            return

        if self.path == '/candidates':
            send_json(self, services.get_candidates())
            return
        m = re.fullmatch(r'/candidates/(\d+)', self.path)
        if m:
            cid = int(m.group(1))
            cand = services.get_candidate(cid)
            if cand:
                send_json(self, cand)
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return

        if self.path == '/comments':
            send_json(self, services.get_comments())
            return
        m = re.fullmatch(r'/comments/(\d+)', self.path)
        if m:
            cid = int(m.group(1))
            com = services.get_comment(cid)
            if com:
                send_json(self, com)
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return

        if self.path == '/evaluations':
            send_json(self, services.get_evaluations())
            return
        m = re.fullmatch(r'/evaluations/(\d+)', self.path)
        if m:
            eid = int(m.group(1))
            ev = services.get_evaluation(eid)
            if ev:
                send_json(self, ev)
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return

        if self.path == '/activities':
            send_json(self, services.get_activities())
            return
        m = re.fullmatch(r'/activities/(\d+)', self.path)
        if m:
            aid = int(m.group(1))
            act = services.get_activity(aid)
            if act:
                send_json(self, act)
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return

        m = re.fullmatch(r'/files/(\d+)', self.path)
        if m:
            if not is_authenticated(self):
                send_json(self, {'error': 'Unauthorized'}, 401)
                return
            fid = int(m.group(1))
            info = services.get_file(fid)
            if info:
                send_file(self, info['path'], info['filename'])
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return

        send_json(self, {'error': 'Unsupported endpoint'}, 404)

    def do_POST(self):
        if self.path == '/files':
            if not is_authenticated(self):
                send_json(self, {'error': 'Unauthorized'}, 401)
                return
            length = int(self.headers.get('Content-Length', 0))
            if length > MAX_FILE_SIZE:
                send_json(self, {'error': 'File too large'}, 400)
                return
            fs = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers.get('Content-Type')},
            )
            fileitem = fs.getfirst('file')
            candidate_id = fs.getfirst('candidate_id')
            if not fileitem or not candidate_id:
                send_json(self, {'error': 'Missing file or candidate_id'}, 400)
                return
            ext = os.path.splitext(fileitem.filename)[1].lower()
            if ext not in ALLOWED_EXTS:
                send_json(self, {'error': 'Invalid file type'}, 400)
                return
            ensure_upload_dir()
            unique_name = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(UPLOAD_DIR, unique_name)
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(fileitem.file, f)
            clamscan = shutil.which('clamscan')
            if clamscan:
                res = subprocess.run([clamscan, '--no-summary', filepath])
                if res.returncode != 0:
                    os.remove(filepath)
                    send_json(self, {'error': 'Malware detected'}, 400)
                    return
            fid = services.create_file(
                {
                    'candidate_id': int(candidate_id),
                    'filename': fileitem.filename,
                    'path': filepath,
                    'uploaded_at': datetime.utcnow().isoformat(),
                }
            )
            send_json(self, {'id': fid}, 201)
            return

        data = parse_body(self)
        if self.path == '/candidates':
            cid = services.create_candidate(data)
            send_json(self, {'id': cid}, 201)
            return
        if self.path == '/comments':
            cid = services.create_comment(data)
            send_json(self, {'id': cid}, 201)
            return
        if self.path == '/evaluations':
            eid = services.create_evaluation(data)
            send_json(self, {'id': eid}, 201)
            return
        if self.path == '/activities':
            aid = services.create_activity(data)
            send_json(self, {'id': aid}, 201)
            return
        send_json(self, {'error': 'Unsupported endpoint'}, 404)

    def do_PUT(self):
        data = parse_body(self)
        m = re.fullmatch(r'/candidates/(\d+)', self.path)
        if m:
            cid = int(m.group(1))
            ok = services.update_candidate(cid, data)
            if ok:
                send_json(self, {'status': 'updated'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        m = re.fullmatch(r'/comments/(\d+)', self.path)
        if m:
            cid = int(m.group(1))
            ok = services.update_comment(cid, data)
            if ok:
                send_json(self, {'status': 'updated'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        m = re.fullmatch(r'/evaluations/(\d+)', self.path)
        if m:
            eid = int(m.group(1))
            ok = services.update_evaluation(eid, data)
            if ok:
                send_json(self, {'status': 'updated'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        m = re.fullmatch(r'/activities/(\d+)', self.path)
        if m:
            aid = int(m.group(1))
            ok = services.update_activity(aid, data)
            if ok:
                send_json(self, {'status': 'updated'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        send_json(self, {'error': 'Unsupported endpoint'}, 404)

    def do_DELETE(self):
        m = re.fullmatch(r'/candidates/(\d+)', self.path)
        if m:
            cid = int(m.group(1))
            ok = services.delete_candidate(cid)
            if ok:
                send_json(self, {'status': 'deleted'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        m = re.fullmatch(r'/comments/(\d+)', self.path)
        if m:
            cid = int(m.group(1))
            ok = services.delete_comment(cid)
            if ok:
                send_json(self, {'status': 'deleted'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        m = re.fullmatch(r'/evaluations/(\d+)', self.path)
        if m:
            eid = int(m.group(1))
            ok = services.delete_evaluation(eid)
            if ok:
                send_json(self, {'status': 'deleted'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        m = re.fullmatch(r'/activities/(\d+)', self.path)
        if m:
            aid = int(m.group(1))
            ok = services.delete_activity(aid)
            if ok:
                send_json(self, {'status': 'deleted'})
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return
        send_json(self, {'error': 'Unsupported endpoint'}, 404)


def run():
    db.init_db()
    ensure_upload_dir()
    server = HTTPServer(('0.0.0.0', 8000), RequestHandler)
    print('Serving on port 8000')
    server.serve_forever()


if __name__ == '__main__':
    run()
