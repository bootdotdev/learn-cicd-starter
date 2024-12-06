package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey_NoAuthHeader(t *testing.T) {
	// Test case where the Authorization header is missing
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("Expected error '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_MalformedAuthHeader(t *testing.T) {
	// Test case where the Authorization header is malformed
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey12345") // Malformed (no space between ApiKey and the actual key)
	_, err := GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("Expected 'malformed authorization header', got '%v'", err)
	}
}

func TestGetAPIKey_ValidAuthHeader(t *testing.T) {
	// Test case where the Authorization header is correctly formatted
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey valid-api-key") // Valid Authorization header
	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Expected no error, got '%v'", err)
	}
	if apiKey != "valid-api-key" {
		t.Errorf("Expected API key 'valid-api-key', got '%v'", apiKey)
	}
}