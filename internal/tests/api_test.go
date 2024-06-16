package tests

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	// Test case 1: No Authorization header
	t.Run("NoAuthHeader", func(t *testing.T) {
		headers := http.Header{}
		apiKey, err := auth.GetAPIKey(headers)
		if err != auth.ErrNoAuthHeaderIncluded {
			t.Errorf("Expected error: %v, got: %v", auth.ErrNoAuthHeaderIncluded, err)
		}
		if apiKey != "" {
			t.Errorf("Expected empty API key, got: %s", apiKey)
		}
	})

	// Test case 2: Malformed Authorization header
	t.Run("MalformedAuthHeader", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "InvalidFormat")
		apiKey, err := auth.GetAPIKey(headers)
		if err == nil || err.Error() != "malformed authorization header" {
			t.Errorf("Expected malformed authorization header error, got: %v", err)
		}
		if apiKey != "" {
			t.Errorf("Expected empty API key, got: %s", apiKey)
		}
	})

	// Test case 3: Valid Authorization header
	t.Run("ValidAuthHeader", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey my-api-key")
		apiKey, err := auth.GetAPIKey(headers)
		if err != nil {
			t.Errorf("Unexpected error: %v", err)
		}
		if apiKey != "my-api-key" {
			t.Errorf("Expected API key 'my-api-key', got: %s", apiKey)
		}
	})
}
