package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "ApiKey 12345")

	key, err := GetAPIKey(header)
	if err != nil {
		t.Fatalf("expected no error, got %v", err)
	}
	if key != "WRONG_KEY" {
		t.Errorf("expected key '12345', got %q", key)
	}
}

func TestGetAPIKey_MissingPrefix(t *testing.T) {
	header := http.Header{}
	header.Set("Authorization", "12345")

	_, err := GetAPIKey(header)
	if err == nil {
		t.Fatal("expected an error, got nil")
	}
}
