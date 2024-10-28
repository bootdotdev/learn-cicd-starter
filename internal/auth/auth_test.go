package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKeySuccess(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey testapikey")

	apiKey, err := GetAPIKey(headers)

	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	if apiKey != "testapikey" {
		t.Errorf("expected 'testapikey', got %v", apiKey)
	}
}

func TestGetAPIKeyNoAuthHeader(t *testing.T) {
	headers := http.Header{}

	_, err := GetAPIKey(headers)

	if !errors.Is(err, ErrNoAuthHeaderIncluded) {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}

func TestGetAPIKeyMalformedAuthHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "Bearer testapikey")

	_, err := GetAPIKey(headers)

	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("expected 'malformed authorization header' error, got %v", err)
	}
}

func TestGetAPIKeyIncompleteAuthHeader(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey")

	_, err := GetAPIKey(headers)

	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("expected 'malformed authorization header' error, got %v", err)
	}
}
