package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected %v, got %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer my-api-key")

	_, err := GetAPIKey(headers)

	if err == nil {
		t.Error("expected error, got nil")
	}
}

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-api-key")

	key, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("expected no error, got %v", err)
	}

	if key != "my-api-key" {
		t.Errorf("expected my-api-key, got %s", key)
	}
}
