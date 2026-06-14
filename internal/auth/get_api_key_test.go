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
		t.Errorf("Expected my-secret-key, got %v", key)
	}
	// Test case: Empty header
	_, err = GetAPIKey(http.Header{})
	if err == nil {
		t.Error("Expected error for empty header, got nil")
	}
}
