const { test, before, after } = require('node:test');
const assert = require('node:assert');
const { server } = require('../src/server');

let port;

before((t, done) => {
  server.listen(0, () => {
    port = server.address().port;
    done();
  });
});

after((t, done) => {
  server.close(done);
});

test('admin can create candidate', async () => {
  const res = await fetch(`http://localhost:${port}/candidates`, {
    method: 'POST',
    headers: { 'x-role': 'admin' }
  });
  assert.strictEqual(res.status, 201);
});

test('manager cannot create candidate', async () => {
  const res = await fetch(`http://localhost:${port}/candidates`, {
    method: 'POST',
    headers: { 'x-role': 'manager' }
  });
  assert.strictEqual(res.status, 403);
});

test('recruiter can read candidates', async () => {
  const res = await fetch(`http://localhost:${port}/candidates`, {
    method: 'GET',
    headers: { 'x-role': 'recruiter' }
  });
  assert.strictEqual(res.status, 200);
});
