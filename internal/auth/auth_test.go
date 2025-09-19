package auth

import (
	"net/http"
	"testing"
)

// Example test for a valid header
func TestGetAPIKeyValid(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
        if key != "my-secret-key" {
		t.Fatalf("expected 'my-secret-key', got %s", key)
	}
}

// Example test for a missing header
func TestGetAPIKeyMissing(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("expected error when Authorization header is missing")
	}
}

