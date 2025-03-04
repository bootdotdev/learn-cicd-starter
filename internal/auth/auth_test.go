package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error when no Authorization header is included, got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer some-token")
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Error("Expected error when header is malformed, got nil")
	}
	expectedError := "malformed authorization header"
	if err.Error() != expectedError {
		t.Errorf("Expected error %q, got %q", expectedError, err.Error())
	}
}

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey valid-api-key")
	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if apiKey != "valid-api-key" {
		t.Errorf("Expected API key 'valid-api-key', got %q", apiKey)
	}
}
