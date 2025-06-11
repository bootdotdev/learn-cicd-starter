package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_ValidHeader(t *testing.T) {
    expected := "test-api-key"
    header := make(http.Header)
    header.Set("Authorization", "ApiKey "+expected)
    got, err := GetAPIKey(header)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if got != expected {
        t.Errorf("expected %q, got %q", expected, got)
    }
}

func TestGetAPIKey_HeaderMissing(t *testing.T) {
    header := make(http.Header)
    got, err := GetAPIKey(header)
    if err == nil {
        t.Fatal("expected error, got nil")
    }
    if got != "" {
        t.Errorf("expected empty string, got %q", got)
    }
}

func TestGetAPIKey_MalformedHeader(t *testing.T) {
    header := make(http.Header)
    header.Set("Authorization", "Bearer sometoken")
    got, err := GetAPIKey(header)
    if err == nil {
        t.Fatal("expected error, got nil")
    }
    if got != "" {
        t.Errorf("expected empty string, got %q", got)
    }
}