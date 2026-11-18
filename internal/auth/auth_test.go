package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey abc123")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if apiKey != "abc123" {
		t.Fatalf("expected apiKey to be 'abc123', got %v", apiKey)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected an error, got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}
