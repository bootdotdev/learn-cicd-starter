package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Valid(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if apiKey != "my-secret-key" {
		t.Errorf("expected API key 'my-secret-key', got '%s'", apiKey)
	}
	t.Errorf("for error", apiKey)
}


func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}
	apiKey, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected error '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
	}
	if apiKey != "" {
		t.Errorf("expected empty API key, got '%s'", apiKey)
	}
}
