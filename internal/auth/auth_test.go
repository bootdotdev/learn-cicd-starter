package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey testkey123")
	key, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("expected no error, got %v", err)
	}
	if key != "testkey123" {
		t.Errorf("expected 'testkey123', got '%s'", key)
	}
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Error("expected error for missing header, got nil")
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer sometoken")
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Error("expected error for malformed header, got nil")
	}

	headers.Set("Authorization", "ApiKey")
	_, err = GetAPIKey(headers)
	if err == nil {
		t.Error("expected error for incomplete ApiKey header, got nil")
	}
}
