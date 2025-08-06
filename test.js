const request = require('supertest');
const app = require('./server');

async function run() {
  try {
    await request(app).post('/register').send({ username: 'alice', password: 'password' }).expect(201);
    const loginRes = await request(app).post('/login').send({ username: 'alice', password: 'password' }).expect(200);
    const cookie = loginRes.headers['set-cookie'];
    await request(app).post('/refresh').set('Cookie', cookie).expect(200);
    console.log('basic auth flow passed');
  } catch (err) {
    console.error('tests failed', err);
    process.exit(1);
  }
}

run();
