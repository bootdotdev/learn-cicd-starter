package auth

import (
	"net/http"
	"testing"
)

// TestGetAPIKey tests the GetAPIKey function.
func TestGetAPIKey(t *testing.T) {
	// Sub-test for a valid, well-formed Authorization header.
	t.Run("Valid API Key", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey my-secret-key")

		key, err := GetAPIKey(headers)
		if err != nil {
			t.Fatalf("expected no error, got %v", err)
		}
		if key != "my-secret-key" {
			t.Errorf("expected key to be 'my-secret-key', got '%s'", key)
		}
	})

	// Sub-test for a missing Authorization header.
	t.Run("No Auth Header", func(t *testing.T) {
		headers := http.Header{}

		_, err := GetAPIKey(headers)
		if err == nil {
			t.Fatal("expected an error, but got none")
		}
		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("expected error '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
		}
	})

	// Sub-test for a malformed Authorization header.
	t.Run("Malformed Auth Header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Bearer some-other-token")

		_, err := GetAPIKey(headers)
		if err == nil {
			t.Fatal("expected an error, but got none")
		}
	})
}
