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
		t.Fatalf("expected no error, got: %v", err)
	}
	if key != "my-secret-key" {
		t.Errorf("expected 'my-secret-key', got: %s", key)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("expected error, got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got: %v", err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer something-wrong")

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatalf("expected error, got nil")
	}
	if err.Error() != "malformed authorization header" {
		t.Errorf("expected malformed authorization header error, got: %v", err)
	}
}
