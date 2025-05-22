package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_NoAuthHeader(t *testing.T) {
	headers := http.Header{}
	key, err := GetAPIKey(headers)

	if key != "" {
		t.Errorf("expected empty key, got %v", key)
	}

	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKey_MalformedHeader_MissingToken(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey")

	key, err := GetAPIKey(headers)

	if key != "" {
		t.Errorf("expected empty key, got %v", key)
	}

	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("expected malformed header error, got %v", err)
	}
}

func TestGetAPIKey_ValidHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey valid_api_key_123")

	key, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("expected no error, get %v", err)
	}

	if key != "valid_api_key_123" {
		t.Errorf("expected 'valid_api_key_123, got %v", key)
	}
}
