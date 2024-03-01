package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test with a valid API key
	t.Run("valid API key", func(t *testing.T) {
		headers := http.Header{}
		headers.Add("Authorization", "ApiKey valid_api_key")
		apiKey, err := GetAPIKey(headers)
		if err != nil {
			t.Errorf("expected no error, got %v", err)
		}
		if apiKey != "valid_api_key" {
			t.Errorf("expected API key 'valid_api_key', got '%s'", apiKey)
		}
	})

	// Test with a missing Authorization header
	t.Run("missing Authorization header", func(t *testing.T) {
		headers := http.Header{}
		apiKey, err := GetAPIKey(headers)
		if err == nil {
			t.Errorf("expected error, got nil")
		}
		if !errors.Is(err, ErrNoAuthHeaderIncluded) {
			t.Errorf("expected error '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
		}
		if apiKey != "" {
			t.Errorf("expected empty API key, got '%s'", apiKey)
		}
	})

	// Test with a malformed Authorization header
	t.Run("malformed Authorization header", func(t *testing.T) {
		headers := http.Header{}
		headers.Add("Authorization", "malformed_header")
		apiKey, err := GetAPIKey(headers)
		if err == nil {
			t.Errorf("expected error, got nil")
		}
		if !strings.Contains(err.Error(), "malformed authorization header") {
			t.Errorf("expected error containing 'malformed authorization header', got '%v'", err)
		}
		if apiKey != "" {
			t.Errorf("expected empty API key, got '%s'", apiKey)
		}
	})
}
