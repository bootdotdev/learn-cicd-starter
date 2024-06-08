package database

import (
	"context"
	"testing"
	"time"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/jmoiron/sqlx"
	"github.com/stretchr/testify/assert"
)

func TestCreateNote(t *testing.T) {
	db, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("failed to create mock database: %v", err)
	}
	defer db.Close()

	q := &Queries{db: sqlx.NewDb(db, "sqlmock")}

	ctx := context.Background()
	arg := CreateNoteParams{
		ID:        "1",
		CreatedAt: time.Now().Format(time.RFC3339),
		UpdatedAt: time.Now().Format(time.RFC3339),
		Note:      "Test Note",
		UserID:    "user1",
	}

	// expect the INSERT query
	mock.ExpectExec("INSERT INTO notes").
		WithArgs(arg.ID, arg.CreatedAt, arg.UpdatedAt, arg.Note, arg.UserID).
		WillReturnResult(sqlmock.NewResult(1, 1))

	// call the function
	err = q.CreateNote(ctx, arg)
	assert.NoError(t, err)

	// ensure all expectations were met
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestGetNote(t *testing.T) {
	db, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("failed to create mock database %v", err)
	}
	defer db.Close()

	q := &Queries{db: sqlx.NewDb(db, "sqlmock")}

	ctx := context.Background()
	expectedNote := Note{
		ID:        "1",
		CreatedAt: time.Now().Format(time.RFC3339),
		UpdatedAt: time.Now().Format(time.RFC3339),
		Note:      "Test Note",
		UserID:    "user1",
	}

	rows := sqlmock.NewRows([]string{"id", "created_at", "updated_at", "note", "user_id"}).
		AddRow(expectedNote.ID, expectedNote.CreatedAt, expectedNote.UpdatedAt, expectedNote.Note, expectedNote.UserID)

	mock.ExpectQuery("SELECT id, created_at, updated_at, note, user_id FROM notes WHERE id = ?").
		WithArgs(expectedNote.ID).
		WillReturnRows(rows)

	note, err := q.GetNote(ctx, expectedNote.ID)
	assert.NoError(t, err)
	assert.Equal(t, expectedNote, note)

	// ensure all expectations were met
	assert.NoError(t, mock.ExpectationsWereMet())
}

func TestGetNotesForUser(t *testing.T) {
	db, mock, err := sqlmock.New()
	if err != nil {
		t.Fatalf("failed to create mock database %v", err)
	}
	defer db.Close()

	q := &Queries{db: sqlx.NewDb(db, "sqlmock")}

	ctx := context.Background()
	expectedNotes := []Note{
		{
			ID:        "1",
			CreatedAt: time.Now().Format(time.RFC3339),
			UpdatedAt: time.Now().Format(time.RFC3339),
			Note:      "Test Note 1",
			UserID:    "user1",
		},
		{
			ID:        "2",
			CreatedAt: time.Now().Format(time.RFC3339),
			UpdatedAt: time.Now().Format(time.RFC3339),
			Note:      "Test Note 2",
			UserID:    "user1",
		},
	}

	rows := sqlmock.NewRows([]string{"id", "created_at", "updated_at", "note", "user_id"}).
		AddRow(expectedNotes[0].ID, expectedNotes[0].CreatedAt, expectedNotes[0].UpdatedAt, expectedNotes[0].Note, expectedNotes[0].UserID).
		AddRow(expectedNotes[1].ID, expectedNotes[1].CreatedAt, expectedNotes[1].UpdatedAt, expectedNotes[1].Note, expectedNotes[1].UserID)

	mock.ExpectQuery("SELECT id, created_at, updated_at, note, user_id FROM notes WHERE user_id = ?").
		WithArgs("user1").
		WillReturnRows(rows)

	notes, err := q.GetNotesForUser(ctx, "user1")
	assert.NoError(t, err)
	assert.Equal(t, expectedNotes, notes)

	assert.NoError(t, mock.ExpectationsWereMet())
}
