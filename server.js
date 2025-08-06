const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const speakeasy = require('speakeasy');
const db = require('./db');

const app = express();
app.use(express.json());
app.use(cookieParser());

const JWT_SECRET = process.env.JWT_SECRET || 'secret';
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || 'refresh_secret';
const ACCESS_TOKEN_EXPIRES = '15m';
const REFRESH_TOKEN_EXPIRES = '7d';

function generateAccessToken(user) {
  return jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: ACCESS_TOKEN_EXPIRES });
}

function generateRefreshToken(user) {
  return jwt.sign({ id: user.id }, JWT_REFRESH_SECRET, { expiresIn: REFRESH_TOKEN_EXPIRES });
}

function authMiddleware(req, res, next) {
  const header = req.headers['authorization'];
  if (!header) return res.sendStatus(401);
  const token = header.split(' ')[1];
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

app.post('/register', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'missing fields' });
  const hashed = await bcrypt.hash(password, 10);
  try {
    db.prepare('INSERT INTO users (username, password) VALUES (?, ?)').run(username, hashed);
    res.sendStatus(201);
  } catch (e) {
    if (e.code === 'SQLITE_CONSTRAINT_UNIQUE') return res.status(409).json({ error: 'user exists' });
    res.status(500).json({ error: 'db error' });
  }
});

app.post('/login', async (req, res) => {
  const { username, password, token } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE username=?').get(username);
  if (!user) return res.status(401).json({ error: 'invalid credentials' });
  const match = await bcrypt.compare(password, user.password);
  if (!match) return res.status(401).json({ error: 'invalid credentials' });
  if (user.twofa_secret) {
    const verified = speakeasy.totp.verify({ secret: user.twofa_secret, encoding: 'base32', token });
    if (!verified) return res.status(401).json({ error: 'invalid 2fa token' });
  }
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);
  const rtHash = await bcrypt.hash(refreshToken, 10);
  db.prepare('UPDATE users SET refresh_token=? WHERE id=?').run(rtHash, user.id);
  res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: true, sameSite: 'strict' });
  res.json({ accessToken });
});

app.post('/refresh', async (req, res) => {
  const token = req.cookies.refreshToken;
  if (!token) return res.sendStatus(401);
  try {
    const payload = jwt.verify(token, JWT_REFRESH_SECRET);
    const user = db.prepare('SELECT * FROM users WHERE id=?').get(payload.id);
    if (!user || !user.refresh_token) return res.sendStatus(403);
    const valid = await bcrypt.compare(token, user.refresh_token);
    if (!valid) return res.sendStatus(403);
    const accessToken = generateAccessToken(user);
    res.json({ accessToken });
  } catch (e) {
    res.sendStatus(403);
  }
});

app.post('/logout', (req, res) => {
  const token = req.cookies.refreshToken;
  if (token) {
    try {
      const payload = jwt.verify(token, JWT_REFRESH_SECRET);
      db.prepare('UPDATE users SET refresh_token=NULL WHERE id=?').run(payload.id);
    } catch (e) {}
  }
  res.clearCookie('refreshToken', { httpOnly: true, secure: true, sameSite: 'strict' });
  res.sendStatus(204);
});

app.post('/2fa/setup', authMiddleware, (req, res) => {
  const secret = speakeasy.generateSecret();
  res.json({ secret: secret.base32 });
});

app.post('/2fa/verify', authMiddleware, (req, res) => {
  const { secret, token } = req.body;
  const verified = speakeasy.totp.verify({ secret, encoding: 'base32', token });
  if (!verified) return res.status(400).json({ error: 'invalid token' });
  db.prepare('UPDATE users SET twofa_secret=? WHERE id=?').run(secret, req.user.id);
  res.sendStatus(200);
});

if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Server running on ${PORT}`));
}

module.exports = app;
