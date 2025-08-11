import os
import json
import tempfile
import threading
import shutil
from http.server import HTTPServer
import http.client
import sys
from pathlib import Path

import pytest

# Set up isolated database and upload directory before importing app
# Ensure project root on path and configure isolated env
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
_db_fd, _db_path = tempfile.mkstemp()
os.close(_db_fd)
os.environ['DB_NAME'] = _db_path
_upload_dir = tempfile.mkdtemp()
os.environ['UPLOAD_DIR'] = _upload_dir

import db
from app import RequestHandler, ensure_upload_dir


def _request(port, method, path, body=None, token=None):
    conn = http.client.HTTPConnection('localhost', port)
    headers = {}
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body)
    if token:
        headers['Authorization'] = f'Bearer {token}'
    conn.request(method, path, body=data, headers=headers)
    resp = conn.getresponse()
    raw = resp.read()
    conn.close()
    if raw:
        payload = json.loads(raw.decode())
    else:
        payload = None
    return resp.status, payload


@pytest.fixture(scope='module')
def server():
    db.init_db()
    ensure_upload_dir()
    httpd = HTTPServer(('localhost', 0), RequestHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield port
    httpd.shutdown()
    thread.join()
    os.remove(_db_path)
    shutil.rmtree(_upload_dir)


def test_candidate_crud(server):
    port = server
    status, data = _request(port, 'POST', '/candidates', {'name': 'Alice', 'email': 'alice@example.com'})
    assert status == 201
    cid = data['id']

    status, data = _request(port, 'GET', '/candidates')
    assert status == 200
    assert any(c['id'] == cid for c in data)

    status, data = _request(port, 'GET', f'/candidates/{cid}')
    assert status == 200
    assert data['name'] == 'Alice'

    status, data = _request(port, 'PUT', f'/candidates/{cid}', {'name': 'Alice Smith', 'email': 'alice.smith@example.com'})
    assert status == 200
    assert data['status'] == 'updated'

    status, data = _request(port, 'DELETE', f'/candidates/{cid}')
    assert status == 200
    assert data['status'] == 'deleted'

    status, _ = _request(port, 'GET', f'/candidates/{cid}')
    assert status == 404


def test_user_crud(server):
    port = server
    status, data = _request(port, 'POST', '/users', {
        'username': 'bob', 'email': 'bob@example.com', 'password': 'pw'
    })
    assert status == 201
    uid = data['id']

    status, data = _request(port, 'POST', '/login', {
        'username': 'bob', 'password': 'pw'
    })
    assert status == 200
    token = data['token']

    status, data = _request(port, 'GET', '/users', token=token)
    assert status == 200
    assert any(u['id'] == uid for u in data)

    status, data = _request(port, 'GET', f'/users/{uid}', token=token)
    assert status == 200
    assert data['username'] == 'bob'

    status, data = _request(port, 'PUT', f'/users/{uid}', {
        'username': 'bobby', 'email': 'bob@example.com'
    }, token=token)
    assert status == 200
    assert data['status'] == 'updated'

    status, data = _request(port, 'DELETE', f'/users/{uid}', token=token)
    assert status == 200
    assert data['status'] == 'deleted'

    status, _ = _request(port, 'GET', f'/users/{uid}', token=token)
    assert status == 404


def test_file_upload(server):
    port = server
    status, data = _request(port, 'POST', '/candidates', {'name': 'Carol', 'email': 'carol@example.com'})
    assert status == 201
    cid = data['id']

    boundary = 'BoundaryTest'
    file_content = b'hello world'
    body = (
        f'--{boundary}\r\n'
        'Content-Disposition: form-data; name="candidate_id"\r\n\r\n'
        f'{cid}\r\n'
        f'--{boundary}\r\n'
        'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
        'Content-Type: text/plain\r\n\r\n'
    ).encode() + file_content + b'\r\n' + f'--{boundary}--\r\n'.encode()

    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': 'Bearer secret-token',
    }
    conn = http.client.HTTPConnection('localhost', port)
    conn.request('POST', '/files', body=body, headers=headers)
    resp = conn.getresponse()
    payload = resp.read()
    conn.close()
    assert resp.status == 201, payload
    data = json.loads(payload.decode())
    fid = data['id']

    conn = http.client.HTTPConnection('localhost', port)
    conn.request('GET', '/files', headers={'Authorization': 'Bearer secret-token'})
    resp = conn.getresponse()
    listing = json.loads(resp.read())
    conn.close()
    assert any(f['id'] == fid for f in listing)
