package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Valid(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 12345")

	key, err := GetAPIKey(headers)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if key != "12345" {
		t.Fatalf("expected 12345, got %s", key)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if err == nil {
		t.Fatalf("expected error, got nil")
	}
}
