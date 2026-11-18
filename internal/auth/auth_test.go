package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("missing header", func(t *testing.T) {
		header := http.Header{}
		_, err := GetAPIKey(header)
		if err == nil {
			t.Error("Expected an error for missing header, got nil")
		}
	})

	t.Run("Malformed Header", func(t *testing.T) {
		header := http.Header{}
		header.Set("Authorization", "ApiKeytest-api-key")
		_, err := GetAPIKey(header)
		if err == nil || err.Error() != "malformed authorization header" {
			t.Fatalf("GetAPIKey() malformed: %v", err)
		}

	})

	t.Run("Valid Header", func(t *testing.T) {
		header := http.Header{}
		header.Set("Authorization", "ApiKey test-api-key")
		got, err := GetAPIKey(header)
		if err != nil {
			t.Fatalf("GetAPIKey() returned an error: %v", err)
		}
		if got != "test-api-key" {
			t.Errorf("GetAPIKey() = %v, want %v", got, "test-api-key")
		}
	})
}
