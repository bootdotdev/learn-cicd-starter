package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("returns API key when header formatted correctly", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey secret123")

		key, err := GetAPIKey(headers)
		if err != nil {
			t.Fatalf("expected no error, got %v", err)
		}
		if key != "secret123" {
			t.Fatalf("expected key 'secret123', got %q", key)
		}
	})

	t.Run("returns error when header missing", func(t *testing.T) {
		headers := http.Header{}

		_, err := GetAPIKey(headers)
		if err == nil {
			t.Fatal("expected error, got nil")
		}
		if !errors.Is(err, ErrNoAuthHeaderIncluded) {
			t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
		}
	})

	t.Run("returns error when header malformed", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Bearer token")

		_, err := GetAPIKey(headers)
		if err == nil {
			t.Fatal("expected error, got nil")
		}
		if err.Error() != "malformed authorization header" {
			t.Fatalf("expected malformed header error, got %v", err)
		}
	})

	t.Run("returns error when API key missing", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey")

		_, err := GetAPIKey(headers)
		if err == nil {
			t.Fatal("expected error, got nil")
		}
		if err.Error() != "malformed authorization header" {
			t.Fatalf("expected malformed header error, got %v", err)
		}
	})
}
