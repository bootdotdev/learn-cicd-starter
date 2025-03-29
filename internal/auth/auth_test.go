package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if key != "my-secret-key" {
		t.Fatalf("expected API key 'my-secret-key', got '%s'", key)
	}
}

func TestGetAPIKey_NoAuthHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected error ErrNoAuthHeaderIncluded, got %v", err)
	}
}
