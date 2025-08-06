const http = require('http');
const { authorize } = require('./authorize');

const candidates = [{ id: 1, name: 'Alice' }];

const server = http.createServer((req, res) => {
  if (req.url === '/candidates' && req.method === 'GET') {
    authorize('read', (req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify(candidates));
    })(req, res);
  } else if (req.url === '/candidates' && req.method === 'POST') {
    authorize('create', (req, res) => {
      candidates.push({ id: candidates.length + 1, name: 'New' });
      res.statusCode = 201;
      res.end('created');
    })(req, res);
  } else {
    res.statusCode = 404;
    res.end('Not Found');
  }
});

module.exports = { server };

if (require.main === module) {
  const port = process.env.PORT || 3000;
  server.listen(port, () => console.log(`Server running on ${port}`));
}
