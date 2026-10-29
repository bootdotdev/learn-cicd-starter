-- +goose Up
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    name TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL
);

-- +goose Down
DROP TABLE users;
