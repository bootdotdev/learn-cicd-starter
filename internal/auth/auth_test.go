package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("Success - Valid API Key", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey my-secret-key")

		apiKey, err := GetAPIKey(headers)
		if err != nil {
			t.Errorf("expected no error, got %v", err)
		}
		if apiKey != "my-secret-key" {
			t.Errorf("expected 'my-secret-key', got '%s'", apiKey)
		}
	})

	t.Run("Error - Missing Authorization Header", func(t *testing.T) {
		headers := http.Header{}

		apiKey, err := GetAPIKey(headers)
		if !errors.Is(err, ErrNoAuthHeaderIncluded) {
			t.Errorf("expected error '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
		}
		if apiKey != "" {
			t.Errorf("expected empty apiKey, got '%s'", apiKey)
		}
	})

	t.Run("Error - Malformed Authorization Header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "Bearer my-secret-key")

		apiKey, err := GetAPIKey(headers)
		if err == nil || err.Error() != "malformed authorization header" {
			t.Errorf("expected 'malformed authorization header' error, got '%v'", err)
		}
		if apiKey != "" {
			t.Errorf("expected empty apiKey, got '%s'", apiKey)
		}
	})

	t.Run("Error - Authorization Header Without Key", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey")

		apiKey, err := GetAPIKey(headers)
		if err == nil || err.Error() != "malformed authorization header" {
			t.Errorf("expected 'malformed authorization header' error, got '%v'", err)
		}
		if apiKey != "" {
			t.Errorf("expected empty apiKey, got '%s'", apiKey)
		}
	})
}
