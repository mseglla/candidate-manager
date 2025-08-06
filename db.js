const Database = require('better-sqlite3');
const db = new Database('data.db');

db.exec(`CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  twofa_secret TEXT,
  refresh_token TEXT
)`);

module.exports = db;
