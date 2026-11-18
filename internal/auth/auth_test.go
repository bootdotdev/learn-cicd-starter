package auth

import (
	"net/http"
	"testing"
)

func TestAuth(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if key != "my-secret-key" {
		t.Errorf("Expected 'my-secret-key', got %v", key)
	}

	// Test missing header
	headers = http.Header{}
	_, err = GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error for missing header, got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}

	// Test malformed header
	headers.Set("Authorization", "Bearer token")
	_, err = GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error for malformed header, got nil")
	}
}
