-- name: CreateNote :exec
INSERT INTO notes (id, created_at, updated_at, note, user_id)
VALUES (?, ?, ?, ?, ?);
--

-- name: GetNote :one
SELECT * FROM notes WHERE id = ?;
--

-- name: GetNotesForUser :many
SELECT * FROM notes WHERE user_id = ?;
--

-- name: UpdateNote :exec
UPDATE notes SET updated_at = ?, note = ? WHERE id = ?;
--

-- name: DeleteNote :exec
DELETE FROM notes WHERE id = ?;
--
