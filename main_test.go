package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func TestExample(t *testing.T) {
	got := 2 + 2
	want := 4

	if got != want {
		t.Errorf("Got %d, want %d", got, want)
	}
}

func TestHandlerReadiness(t *testing.T) {
	req := httptest.NewRequest("GET", "/v1/healthz", nil)
	w := httptest.NewRecorder()

	handlerReadiness(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status code %d, got %d", http.StatusOK, w.Code)
	}

	expectedBody := `{"status":"ok"}`
	if strings.TrimSpace(w.Body.String()) != expectedBody {
		t.Errorf("Expected body %s, got %s", expectedBody, w.Body.String())
	}

	contentType := w.Header().Get("Content-Type")
	if contentType != "application/json" {
		t.Errorf("Expected Content-Type 'application/json', got %s", contentType)
	}
}

func TestGenerateRandomSHA256Hash(t *testing.T) {
	hash1, err := generateRandomSHA256Hash()
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	if len(hash1) != 64 {
		t.Errorf("Expected hash length of 64, got %d", len(hash1))
	}

	// Generate a second hash to ensure they are different (randomness test)
	hash2, err := generateRandomSHA256Hash()
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	if hash1 == hash2 {
		t.Error("Generated hashes should be different (randomness check)")
	}

	// Test that hash only contains valid hex characters
	for _, r := range hash1 {
		if !((r >= '0' && r <= '9') || (r >= 'a' && r <= 'f')) {
			t.Errorf("Hash contains invalid character: %c", r)
		}
	}
}

func TestRespondWithJSON(t *testing.T) {
	tests := []struct {
		name           string
		payload        interface{}
		statusCode     int
		expectedBody   string
	}{
		{
			name:         "simple map",
			payload:      map[string]string{"status": "ok"},
			statusCode:   200,
			expectedBody: `{"status":"ok"}`,
		},
		{
			name:         "string payload",
			payload:      "hello",
			statusCode:   200,
			expectedBody: `"hello"`,
		},
		{
			name:         "number payload",
			payload:      42,
			statusCode:   200,
			expectedBody: `42`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			respondWithJSON(w, tt.statusCode, tt.payload)

			if w.Code != tt.statusCode {
				t.Errorf("Expected status code %d, got %d", tt.statusCode, w.Code)
			}

			if strings.TrimSpace(w.Body.String()) != tt.expectedBody {
				t.Errorf("Expected body %s, got %s", tt.expectedBody, w.Body.String())
			}

			contentType := w.Header().Get("Content-Type")
			if contentType != "application/json" {
				t.Errorf("Expected Content-Type 'application/json', got %s", contentType)
			}
		})
	}
}

func TestRespondWithError(t *testing.T) {
	tests := []struct {
		name         string
		code         int
		msg          string
		logErr       error
		expectedBody string
	}{
		{
			name:         "400 error without log error",
			code:         400,
			msg:          "Bad request",
			logErr:       nil,
			expectedBody: `{"error":"Bad request"}`,
		},
		{
			name:         "500 error with log error",
			code:         500,
			msg:          "Internal server error",
			logErr:       nil,
			expectedBody: `{"error":"Internal server error"}`,
		},
		{
			name:         "404 error",
			code:         404,
			msg:          "Not found",
			logErr:       nil,
			expectedBody: `{"error":"Not found"}`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			respondWithError(w, tt.code, tt.msg, tt.logErr)

			if w.Code != tt.code {
				t.Errorf("Expected status code %d, got %d", tt.code, w.Code)
			}

			if strings.TrimSpace(w.Body.String()) != tt.expectedBody {
				t.Errorf("Expected body %s, got %s", tt.expectedBody, w.Body.String())
			}

			contentType := w.Header().Get("Content-Type")
			if contentType != "application/json" {
				t.Errorf("Expected Content-Type 'application/json', got %s", contentType)
			}
		})
	}
}

func TestDatabaseUserToUser(t *testing.T) {
	tests := []struct {
		name        string
		dbUser      database.User
		expectError bool
	}{
		{
			name: "valid user conversion",
			dbUser: database.User{
				ID:        "123",
				CreatedAt: "2023-01-01T00:00:00Z",
				UpdatedAt: "2023-01-01T00:00:00Z",
				Name:      "Test User",
				ApiKey:    "test-api-key",
			},
			expectError: false,
		},
		{
			name: "invalid created_at format",
			dbUser: database.User{
				ID:        "123",
				CreatedAt: "invalid-date",
				UpdatedAt: "2023-01-01T00:00:00Z",
				Name:      "Test User",
				ApiKey:    "test-api-key",
			},
			expectError: true,
		},
		{
			name: "invalid updated_at format",
			dbUser: database.User{
				ID:        "123",
				CreatedAt: "2023-01-01T00:00:00Z",
				UpdatedAt: "invalid-date",
				Name:      "Test User",
				ApiKey:    "test-api-key",
			},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			user, err := databaseUserToUser(tt.dbUser)

			if tt.expectError {
				if err == nil {
					t.Error("Expected error but got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("Unexpected error: %v", err)
				return
			}

			if user.ID != tt.dbUser.ID {
				t.Errorf("Expected ID %s, got %s", tt.dbUser.ID, user.ID)
			}

			if user.Name != tt.dbUser.Name {
				t.Errorf("Expected Name %s, got %s", tt.dbUser.Name, user.Name)
			}

			if user.ApiKey != tt.dbUser.ApiKey {
				t.Errorf("Expected ApiKey %s, got %s", tt.dbUser.ApiKey, user.ApiKey)
			}
		})
	}
}

func TestDatabaseNoteToNote(t *testing.T) {
	tests := []struct {
		name        string
		dbNote      database.Note
		expectError bool
	}{
		{
			name: "valid note conversion",
			dbNote: database.Note{
				ID:        "note-123",
				CreatedAt: "2023-01-01T00:00:00Z",
				UpdatedAt: "2023-01-01T00:00:00Z",
				Note:      "This is a test note",
				UserID:    "user-123",
			},
			expectError: false,
		},
		{
			name: "invalid created_at format",
			dbNote: database.Note{
				ID:        "note-123",
				CreatedAt: "invalid-date",
				UpdatedAt: "2023-01-01T00:00:00Z",
				Note:      "This is a test note",
				UserID:    "user-123",
			},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			note, err := databaseNoteToNote(tt.dbNote)

			if tt.expectError {
				if err == nil {
					t.Error("Expected error but got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("Unexpected error: %v", err)
				return
			}

			if note.ID != tt.dbNote.ID {
				t.Errorf("Expected ID %s, got %s", tt.dbNote.ID, note.ID)
			}

			if note.Note != tt.dbNote.Note {
				t.Errorf("Expected Note %s, got %s", tt.dbNote.Note, note.Note)
			}

			if note.UserID != tt.dbNote.UserID {
				t.Errorf("Expected UserID %s, got %s", tt.dbNote.UserID, note.UserID)
			}
		})
	}
}

func TestDatabasePostsToPosts(t *testing.T) {
	tests := []struct {
		name        string
		dbNotes     []database.Note
		expectError bool
		expectedLen int
	}{
		{
			name: "valid notes conversion",
			dbNotes: []database.Note{
				{
					ID:        "note-1",
					CreatedAt: "2023-01-01T00:00:00Z",
					UpdatedAt: "2023-01-01T00:00:00Z",
					Note:      "First note",
					UserID:    "user-1",
				},
				{
					ID:        "note-2",
					CreatedAt: "2023-01-02T00:00:00Z",
					UpdatedAt: "2023-01-02T00:00:00Z",
					Note:      "Second note",
					UserID:    "user-2",
				},
			},
			expectError: false,
			expectedLen: 2,
		},
		{
				name:        "empty notes slice",
				dbNotes:     []database.Note{},
				expectError: false,
				expectedLen: 0,
			},
			{
				name: "invalid note in slice",
				dbNotes: []database.Note{
					{
						ID:        "note-1",
						CreatedAt: "invalid-date",
						UpdatedAt: "2023-01-01T00:00:00Z",
						Note:      "First note",
						UserID:    "user-1",
					},
				},
				expectError: true,
				expectedLen: 0,
			},
		}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			notes, err := databasePostsToPosts(tt.dbNotes)

			if tt.expectError {
				if err == nil {
					t.Error("Expected error but got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("Unexpected error: %v", err)
				return
			}

			if len(notes) != tt.expectedLen {
				t.Errorf("Expected length %d, got %d", tt.expectedLen, len(notes))
			}

			for i, note := range notes {
				if i < len(tt.dbNotes) {
					if note.ID != tt.dbNotes[i].ID {
						t.Errorf("Expected note %d ID %s, got %s", i, tt.dbNotes[i].ID, note.ID)
					}
					if note.Note != tt.dbNotes[i].Note {
						t.Errorf("Expected note %d Note %s, got %s", i, tt.dbNotes[i].Note, note.Note)
					}
				}
			}
		})
	}
}
