package auth

import (
    "net/http"
    "testing"
)

func TestGetAPIKey_HeaderMissing(t *testing.T) {
    headers := http.Header{}
    _, err := GetAPIKey(headers)
    if err != ErrNoAuthHeaderIncluded {
        t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
    }
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "Bearer something")
    _, err := GetAPIKey(headers)
    if err == nil || err.Error() != "malformed authorization header" {
        t.Errorf("expected malformed authorization header error, got %v", err)
    }
}

func TestGetAPIKey_Success(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "ApiKey my-real-key")
    apiKey, err := GetAPIKey(headers)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if apiKey != "my-real-key" {
        t.Errorf("expected 'my-real-key', got '%s'", apiKey)
    }
}