package auth

import (
	"errors"
	"net/http"
	"testing"
)

// TestGetAPIKey_ValidHeader tests the function with a correct Authorization header.
func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got: %v", err)
	}
	if apiKey != "my-secret-key" {
		t.Fatalf("expected API key to be 'my-secret-key', got: %s", apiKey)
	}
}

// TestGetAPIKey_MissingHeader tests the function when no Authorization header is provided.
func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	apiKey, err := GetAPIKey(headers)

	if apiKey != "" {
		t.Fatalf("expected empty API key, got: %s", apiKey)
	}
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got: %v", err)
	}
}

// TestGetAPIKey_MalformedHeader tests the function when the Authorization header is malformed.
func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer my-secret-key") // Incorrect prefix

	apiKey, err := GetAPIKey(headers)

	if apiKey != "" {
		t.Fatalf("expected empty API key, got: %s", apiKey)
	}
	if err == nil || err.Error() != "malformed authorization header" {
		t.Fatalf("expected 'malformed authorization header' error, got: %v", err)
	}
}

// TestGetAPIKey_EmptyAuthValue tests when "Authorization" is present but doesn't contain an API key.
func TestGetAPIKey_EmptyAuthValue(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey")

	apiKey, err := GetAPIKey(headers)

	if apiKey != "" {
		t.Fatalf("expected empty API key, got: %s", apiKey)
	}
	if err == nil || err.Error() != "malformed authorization header" {
		t.Fatalf("expected 'malformed authorization header' error, got: %v", err)
	}
}
