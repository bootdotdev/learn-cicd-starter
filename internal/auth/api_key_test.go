package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer 12345")

	_, err := GetAPIKey(headers)

	if err == nil {
		t.Error("expected error for malformed header, got nil")
	}
}

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	apiKey, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	if apiKey != "my-secret-key" {
		t.Errorf("expected 'my-secret-key', got %s", apiKey)
	}
}
