package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)


func TestGetAPIKey_Valid(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "ApiKey valid-api-key")

    apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if apiKey != "valid-api-key" {
		t.Fatalf("Expected API key to be 'valid-api-key', got %v", apiKey)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey valid-api-key")

	_, err := GetAPIKey(headers)
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Fatalf("Expected error '%v', got %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer malformed-api-key")

	_, err := GetAPIKey(headers)
	if !strings.Contains(err.Error(), "malformed authorization header") {
		t.Fatalf("Expected malformed authorization header error, got %v", err)
	}
}