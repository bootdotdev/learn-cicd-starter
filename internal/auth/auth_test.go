package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "ApiKey 12345")

	key, err := GetAPIKey(h)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if key != "12345" {
		t.Errorf("expected 12345, got %q", key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	h := http.Header{}
	_, err := GetAPIKey(h)
	if err == nil {
		t.Fatalf("expected error for missing Authorization header")
	}
}

func TestGetAPIKey_WrongScheme(t *testing.T) {
	h := http.Header{}
	h.Set("Authorization", "Bearer 12345")

	_, err := GetAPIKey(h)
	if err == nil {
		t.Fatalf("expected error for wrong scheme")
	}
}

