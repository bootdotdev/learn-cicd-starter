package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeyValidHeader(t *testing.T) {
    headers := http.Header{"Authorization": []string{"ApiKey my-api-key"}}
    apiKey, err := GetAPIKey(headers)
    if err != nil {
        t.Errorf("expected no error, got %v", err)
    }
    expectedAPIKey := "my-api-key"
    if apiKey != expectedAPIKey {
        t.Errorf("expected API key %q, got %q", expectedAPIKey, apiKey)
    }
}

func TestGetAPIKeyNoAuthHeader(t *testing.T) {
    headers := http.Header{}
    _, err := GetAPIKey(headers)
    if err != ErrNoAuthHeaderIncluded {
        t.Errorf("expected error %q, got %v", ErrNoAuthHeaderIncluded, err)
    }
}

func TestGetAPIKeyMalformedHeader(t *testing.T) {
    headers := http.Header{"Authorization": []string{"Bearer token"}}
    _, err := GetAPIKey(headers)
    if err == nil {
        t.Error("expected error, got nil")
    }
}
