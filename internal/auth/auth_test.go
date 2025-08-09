package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey testtoken123")

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got: %v", err)
	}
	if key != "testtoken123" {
		t.Errorf("expected key to be 'testtoken123', got: %s", 
key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error for missing header, got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got: %v", err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer sometoken")

	_, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error for malformed header, got nil")
	}
}

