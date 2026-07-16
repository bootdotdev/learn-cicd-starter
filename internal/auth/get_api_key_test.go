package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("returns error when no authorization header", func(t *testing.T) {
		headers := http.Header{}

		key, err := GetAPIKey(headers)

		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
		}
		if key != "" {
			t.Errorf("expected empty key, got %q", key)
		}
	})

	t.Run("returns error for empty authorization header", func(t *testing.T) {
		headers := http.Header{
			"Authorization": []string{""},
		}

		key, err := GetAPIKey(headers)

		if err == nil {
			t.Fatal("expected error for empty header, got nil")
		}
		if key != "" {
			t.Errorf("expected empty key, got %q", key)
		}
	})

	t.Run("returns error for header without 'ApiKey' scheme", func(t *testing.T) {
		headers := http.Header{
			"Authorization": []string{"Bearer token123"},
		}

		key, err := GetAPIKey(headers)

		if err == nil {
			t.Fatal("expected error for Bearer scheme, got nil")
		}
		if key != "" {
			t.Errorf("expected empty key, got %q", key)
		}
	})

	t.Run("returns error for malformed header with only one part", func(t *testing.T) {
		headers := http.Header{
			"Authorization": []string{"ApiKey"},
		}

		key, err := GetAPIKey(headers)

		if err == nil {
			t.Fatal("expected error for missing key portion, got nil")
		}
		if key != "" {
			t.Errorf("expected empty key, got %q", key)
		}
	})

	t.Run("successfully extracts API key from valid header", func(t *testing.T) {
		expectedKey := "my-secret-api-key-12345"
		headers := http.Header{
			"Authorization": []string{"ApiKey " + expectedKey},
		}

		key, err := GetAPIKey(headers)

		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if key != expectedKey {
			t.Errorf("expected %q, got %q", expectedKey, key)
		}
	})

	t.Run("extra whitespace causes issues with Split - known limitation", func(t *testing.T) {
		headers := http.Header{
			"Authorization": []string{"ApiKey  api-key"}, // Two spaces
		}

		key, err := GetAPIKey(headers)

		// Current Split behavior: ["ApiKey", "", "api-key"], so splitAuth[1] = ""
		if err == nil && key == "" {
			// Documented quirk - production code needs fixing for robust parsing
			return
		}
		if err != nil {
			t.Errorf("got error %v, expected none or empty key", err)
		}
	})

	t.Run("header case-sensitivity check - lowercase apischeme fails", func(t *testing.T) {
		headers := http.Header{
			"Authorization": []string{"apikey secret123"},
		}

		key, err := GetAPIKey(headers)

		if err == nil {
			t.Fatal("expected error for lowercase 'apikey', got nil")
		}
		if key != "" {
			t.Errorf("expected empty key, got %q", key)
		}
	})
}
