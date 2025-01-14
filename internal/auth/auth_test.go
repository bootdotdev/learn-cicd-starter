package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("Authorization header with valid ApiKey", func(t *testing.T) {
		// Arrange
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey test-key")

		// Act
		apiKey, err := GetAPIKey(headers)

		// Assert
		if err != nil {
			t.Errorf("unexpected error: %v", err)
		}
		if apiKey != "test-key" {
			t.Errorf("expected 'test-key', got '%s'", apiKey)
		}
	})

	t.Run("Authorization header missing", func(t *testing.T) {
		// Arrange
		headers := http.Header{}

		// Act
		apiKey, err := GetAPIKey(headers)

		// Assert
		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
		}
		if apiKey != "" {
			t.Errorf("expected empty string, got '%s'", apiKey)
		}
	})
}
