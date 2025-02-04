package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("valid API key exists in the context", func(t *testing.T) {
		headers := make(http.Header)
		headers.Add("Authorization", "ApiKey test-key-123")

		got, err := GetAPIKey(headers)
		if err != nil {
			t.Errorf("expected no error, got %v", err)
		}

		want := "test-key-123"
		if got != want {
			t.Errorf("got %q, want %q", got, want)
		}
	})
	t.Run("no API key exists", func(t *testing.T) {
		headers := make(http.Header)
		// Don't add any Authorization header

		got, err := GetAPIKey(headers)
		if err == ErrNoAuthHeaderIncluded {
			t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
		}

		if got != "" {
			t.Errorf("Expected empty string, got %v", got)
		}

	})
	t.Run("malformed authorization header", func(t *testing.T) {
		headers := make(http.Header)
		headers.Add("Authorization", "Bearer test-key-123") // Wrong prefix

		got, err := GetAPIKey(headers)
		if err == nil {
			t.Error("expected error, got nil")
		}
		if err.Error() != "malformed authorization header" {
			t.Errorf("expected 'malformed authorization header', got %v", err)
		}
		if got != "" {
			t.Errorf("expected empty string, got %q", got)
		}
	})
}
