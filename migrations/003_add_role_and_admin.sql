ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user';
INSERT OR IGNORE INTO users (username, email, password, role)
VALUES ('admin', 'admin@example.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');
