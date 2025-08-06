import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import db
import services


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

        send_json(self, {'error': 'Unsupported endpoint'}, 404)

    def do_POST(self):
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
    server = HTTPServer(('0.0.0.0', 8000), RequestHandler)
    print('Serving on port 8000')
    server.serve_forever()


if __name__ == '__main__':
    run()
