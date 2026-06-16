package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test case: Valid header
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")
	key, err := GetAPIKey(headers)
	if err != nil || key != "my-secret-key" {
		t.Errorf("Expected 'my-secret-key', got '%s'", key)
	}

	// Test case: Missing header
	headers = http.Header{}
	_, err = GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error for missing Authorization header, got nil")
	}
}
