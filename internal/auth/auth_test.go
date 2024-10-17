package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
    headers := http.Header{}
    headers.Add("Authorization", "ApiKey 123")
    key, err := GetAPIKey(headers)
    if err != nil {
        t.Fatalf("expected nil, got %v", err)
    }
    if key != "123" {
        t.Fatalf("expected 123, got %s", key)
    }
}