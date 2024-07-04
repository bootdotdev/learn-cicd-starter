package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test case 1: Valid API key
	t.Run("Valid API Key", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey valid_api_key")
		apiKey, err := GetAPIKey(headers)
		if err != nil {
			t.Errorf("Unexpected error: %v", err)
		}
		if apiKey != "valid_api_key" {
			t.Errorf("Expected API key: valid_api_key, got: %s", apiKey)
		}
	})

	// Test case 2: Missing authorization header
	t.Run("Missing Authorization Header", func(t *testing.T) {
		headers := http.Header{}
		apiKey, err := GetAPIKey(headers)
		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("Expected error: %v, got: %v", ErrNoAuthHeaderIncluded, err)
		}
		if apiKey != "" {
			t.Errorf("Expected empty API key, got: %s", apiKey)
		}
	})

	// Test case 3: Malformed authorization header
	t.Run("Malformed Authorization Header", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "InvalidPrefix valid_api_key")
		apiKey, err := GetAPIKey(headers)
		if err == nil {
			t.Error("Expected an error, got nil")
		}
		if err.Error() != "malformed authorization header" {
			t.Errorf("Expected error message: malformed authorization header, got: %s", err.Error())
		}
		if apiKey != "" {
			t.Errorf("Expected empty API key, got: %s", apiKey)
		}
	})
}
