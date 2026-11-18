package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("returns key when header is valid", func(t *testing.T) {
		h := http.Header{}
		h.Set("Authorization", "ApiKey abc123")
		got, err := GetAPIKey(h)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got != "abc123" {
			t.Fatalf("expected abc123, got %q", got)
		}
	})

	t.Run("returns ErrNoAuthHeaderIncluded when header missing", func(t *testing.T) {
		h := http.Header{}
		_, err := GetAPIKey(h)
		if err != ErrNoAuthHeaderIncluded {
			t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
		}
	})

	t.Run("returns error when header malformed", func(t *testing.T) {
		h := http.Header{}
		h.Set("Authorization", "Bearer abc123")
		_, err := GetAPIKey(h)
		if err == nil {
			t.Fatalf("expected error for malformed header, got nil")
		}
	})
}
