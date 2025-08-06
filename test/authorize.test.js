const test = require('node:test');
const assert = require('node:assert');
const { authorize } = require('../src/authorize');

function makeRes() {
  return {
    statusCode: 200,
    ended: false,
    end() { this.ended = true; },
    setHeader() {}
  };
}

test('authorize allows action when role has permission', () => {
  const req = { headers: { 'x-role': 'admin' } };
  const res = makeRes();
  let called = false;
  authorize('create', () => { called = true; })(req, res);
  assert.ok(called);
  assert.strictEqual(res.statusCode, 200);
});

test('authorize denies action when role lacks permission', () => {
  const req = { headers: { 'x-role': 'recruiter' } };
  const res = makeRes();
  authorize('delete', () => { throw new Error('should not call'); })(req, res);
  assert.strictEqual(res.statusCode, 403);
  assert.ok(res.ended);
});
