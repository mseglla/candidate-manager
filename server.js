const http = require('http');
const fs = require('fs');
const path = require('path');

let candidates = [];
let nextId = 1;

function serveStaticFile(req, res) {
  let filePath = req.url === '/' ? '/index.html' : req.url;
  filePath = path.join(__dirname, 'public', filePath);
  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
    } else {
      const ext = path.extname(filePath).toLowerCase();
      const mime = {
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.json': 'application/json'
      }[ext] || 'text/plain';
      res.writeHead(200, { 'Content-Type': mime });
      res.end(content);
    }
  });
}

function handleApi(req, res) {
  if (req.method === 'GET' && req.url === '/api/candidates') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(candidates));
  } else if (req.method === 'POST' && req.url === '/api/candidates') {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
    });
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const candidate = { id: nextId++, name: data.name, email: data.email };
        candidates.push(candidate);
        res.writeHead(201, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(candidate));
      } catch (e) {
        res.writeHead(400);
        res.end('Invalid JSON');
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith('/api/')) {
    handleApi(req, res);
  } else {
    serveStaticFile(req, res);
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
