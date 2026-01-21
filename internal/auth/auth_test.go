package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "ApiKey abc123")

	key, err := GetAPIKey(h)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if key != "abc123" {
		t.Fatalf("expected key %q, got %q", "abc123", key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	h := http.Header{}

	_, err := GetAPIKey(h)
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_WrongScheme(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "Bearer abc123")

	_, err := GetAPIKey(h)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "ApiKey")

	_, err := GetAPIKey(h)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}
