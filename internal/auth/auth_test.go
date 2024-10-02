package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	// Set up headers with a valid "Authorization" header
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey valid-key")

	// Call the function under test
	result, err := GetAPIKey(headers)

	// Check the results
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if result != "valid-key" {
		t.Errorf("expected 'valid-key', got %v", result)
	}
}
