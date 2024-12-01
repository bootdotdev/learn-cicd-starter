package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_NoHeader(t *testing.T) {
	_, err := GetAPIKey(http.Header{})
	if err != ErrNoAuthHeaderIncluded {
		t.Fatalf("expected err: %v, got: %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_InvalidAuthHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer 123")
	_, err := GetAPIKey(headers)
	if err != ErrInvalidAuthHeader {
		t.Fatalf("expected err: %v, got: %v", ErrInvalidAuthHeader, err)
	}
}

func TestGetAPIKey_OK(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey 123")
	key, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("expected err: %v, got: %v", nil, err)
	}
	if key != "123" {
		t.Fatalf("expected err: %v, got: %v", "123", key)
	}
}
