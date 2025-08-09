import json
import re
import os
import uuid
import cgi
import mimetypes
import shutil
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import db
import services


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
API_TOKEN = os.getenv("API_TOKEN", "secret-token")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}


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


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.chmod(UPLOAD_DIR, 0o700)


def is_authorized(handler):
    auth = handler.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        if token == API_TOKEN:
            return True
    send_json(handler, {"error": "Unauthorized"}, 401)
    return False


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

        if self.path == '/users':
            send_json(self, services.get_users())
            return
        m = re.fullmatch(r'/users/(\d+)', self.path)
        if m:
            uid = int(m.group(1))
            user = services.get_user(uid)
            if user:
                send_json(self, user)
            else:
                send_json(self, {'error': 'Not found'}, 404)
            return

        if self.path == '/files':
            if not is_authorized(self):
                return
            send_json(self, services.get_files())
            return
        m = re.fullmatch(r'/files/(\d+)', self.path)
        if m:
            if not is_authorized(self):
                return
            fid = int(m.group(1))
            f = services.get_file(fid)
            if not f:
                send_json(self, {'error': 'Not found'}, 404)
                return
            path = f['path']
            abs_path = os.path.abspath(path)
            if not abs_path.startswith(os.path.abspath(UPLOAD_DIR)):
                send_json(self, {'error': 'Invalid path'}, 400)
                return
            try:
                with open(abs_path, 'rb') as fp:
                    data = fp.read()
            except FileNotFoundError:
                send_json(self, {'error': 'Not found'}, 404)
                return
            self.send_response(200)
            mime = mimetypes.guess_type(f['filename'])[0] or 'application/octet-stream'
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Content-Disposition', f'attachment; filename="{f["filename"]}"')
            self.end_headers()
            self.wfile.write(data)
            return

    def do_POST(self):
        if self.path == '/files':
            if not is_authorized(self):
                return
            ctype = self.headers.get('Content-Type', '')
            if not ctype.startswith('multipart/form-data'):
                send_json(self, {'error': 'Content-Type must be multipart/form-data'}, 400)
                return
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': ctype})
            if 'file' not in form or not form['file'].filename:
                send_json(self, {'error': 'file field required'}, 400)
                return
            candidate_id = form.getvalue('candidate_id')
            if not candidate_id:
                send_json(self, {'error': 'candidate_id required'}, 400)
                return
            try:
                candidate_id = int(candidate_id)
            except ValueError:
                send_json(self, {'error': 'invalid candidate_id'}, 400)
                return
            file_item = form['file']
            filename = os.path.basename(file_item.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                send_json(self, {'error': 'Invalid file extension'}, 400)
                return
            file_data = file_item.file.read()
            if len(file_data) > MAX_FILE_SIZE:
                send_json(self, {'error': 'File too large'}, 400)
                return
            unique_name = f"{uuid.uuid4().hex}{ext}"
            dest_path = os.path.join(UPLOAD_DIR, unique_name)
            with open(dest_path, 'wb') as f:
                f.write(file_data)
            scanner = shutil.which('clamscan')
            if scanner:
                result = subprocess.run([scanner, dest_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    os.remove(dest_path)
                    send_json(self, {'error': 'Malware detected'}, 400)
                    return
            fid = services.create_file({
                'candidate_id': candidate_id,
                'filename': filename,
                'path': dest_path,
                'uploaded_at': datetime.utcnow().isoformat()
            })
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
        if self.path == '/users':
            uid = services.create_user(data)
            send_json(self, {'id': uid}, 201)
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
        m = re.fullmatch(r'/users/(\d+)', self.path)
        if m:
            uid = int(m.group(1))
            ok = services.update_user(uid, data)
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
        m = re.fullmatch(r'/users/(\d+)', self.path)
        if m:
            uid = int(m.group(1))
            ok = services.delete_user(uid)
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
