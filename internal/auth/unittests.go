package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	expectedKey := "secret-key-123"
	headers.Set("Authorization", "ApiKey "+expectedKey)

	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}

	if key != expectedKey {
		t.Errorf("expected key %q, got %q", expectedKey, key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}

	key, err := GetAPIKey(headers)
	if err == nil {
		t.Fatal("expected error, got nil")
	}

	if key != "" {
		t.Errorf("expected empty key, got %q", key)
	}

	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
	}
}
