-- +goose Up
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- +goose Down
DROP TABLE notes;
DROP TABLE users;

