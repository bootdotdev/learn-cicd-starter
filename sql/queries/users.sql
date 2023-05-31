-- name: CreateUser :exec
INSERT INTO users (id, created_at, updated_at, name, api_key)
VALUES (
    ?,
    ?,
    ?,
    ?,
    ?
);
--

-- name: GetUserByAPIKey :one
SELECT * FROM users WHERE api_key = ?;
--
