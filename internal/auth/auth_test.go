package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Success(t *testing.T) {
	headers := http.Header{}
	expectedAPIKey := "abcdef123456"
	headers.Set("Authorization", "ApiKey "+expectedAPIKey)

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("expected no error, but got: %v", err)
	}
	if apiKey != expectedAPIKey {
		t.Errorf("expected API key %q, but got %q", expectedAPIKey, apiKey)
	}
}

func TestGetAPIKey_NoHeader(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Error("expected error because no Authorization header was included, but got nil")
	}
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected error %v, but got %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
	headers := http.Header{}

	// Test with a header that contains only one part.
	headers.Set("Authorization", "ApiKey")
	_, err := GetAPIKey(headers)
	if err == nil {
		t.Error("expected error for malformed header (only one part), but got nil")
	}

	// Test with an Authorization scheme other than "ApiKey".
	headers.Set("Authorization", "Bearer some-token")
	_, err = GetAPIKey(headers)
	if err == nil {
		t.Error("expected error for malformed header (wrong auth scheme), but got nil")
	}

	// Test with a header where the first part is not "ApiKey".
	headers.Set("Authorization", "NotApiKey sometoken")
	_, err = GetAPIKey(headers)
	if err == nil {
		t.Error("expected error for malformed header (incorrect auth type), but got nil")
	}
}
