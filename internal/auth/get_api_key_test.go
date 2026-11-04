package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyValid(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey test-api-key")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if key != "test-api-key" {
		t.Errorf("expected %q, got %q", "test-api-key", key)
	}
}

func TestGetAPIKeyMissingHeader(t *testing.T) {
	headers := http.Header{}

	key, err := GetAPIKey(headers)

	if err == nil {
		t.Fatal("expected an error, got nil")
	}

	if key != "" {
		t.Errorf("expected empty API key, got %q", key)
	}
}
