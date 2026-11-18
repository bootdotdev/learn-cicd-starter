package auth

import (
    "net/http"
    "testing"
)

func TestGetAPIKey_Success(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "ApiKey test123")

    key, err := GetAPIKey(headers)
    if err != nil {
        t.Fatalf("expected no error, got %v", err)
    }
    if key != "test123" {
        t.Errorf("expected key to be 'test123', got '%s'", key)
    }
}

func TestGetAPIKey_MissingHeader(t *testing.T) {
    headers := http.Header{}

    _, err := GetAPIKey(headers)
    if err == nil {
        t.Fatal("expected an error when header is missing, got nil")
    }
}
