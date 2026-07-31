package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "ApiKey somekeyvalue")

    gotKey, err := GetAPIKey(headers)
    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }
    if gotKey != "somekeyvalue" {
        t.Errorf("got %q, want %q", gotKey, "somekeyvalue")
    }
}

func TestGetAPIKey_WrongPrefix(t *testing.T) {
    headers := http.Header{}
    headers.Set("Authorization", "Bearer abc123")

    gotKey, err := GetAPIKey(headers)
    if err == nil {
        t.Errorf("unexpected error: %v", err)
    }
    if gotKey != "" {
        t.Errorf("got %q, want %q", gotKey, "")
    }
}