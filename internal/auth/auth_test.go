package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_FailsWithoutApiKeyEntry(t *testing.T) {
	headers := make(http.Header)
	headers.Set("Authorization", "Bearer 1234")
	_, err := GetAPIKey(headers)
	if err != ErrMalformedAuthHeader {
		t.Errorf("Expected error %v, got %v", ErrMalformedAuthHeader, err)
	}
}

func TestGetAPIKey_FailsWithoutAuthHeader(t *testing.T) {
	headers := make(http.Header)
	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
	}
}

func TestGetAPIKey_Success(t *testing.T) {
	headers := make(http.Header)
	headers.Set("Authorization", "ApiKey 1234")
	key, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if key == "1234" {
		t.Errorf("Expected key to be 1234, got %v", key)
	}
}
