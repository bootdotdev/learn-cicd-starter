package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	got, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if got != "my-secret-key" {
		t.Fatalf("expected API key %q, got %q", "my-secret-key", got)
	}
}

func TestGetAPIKeyNoAuthHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}
