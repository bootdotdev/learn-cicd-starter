package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
    headers := http.Header{}
    headers.Add("Authorization", "ApiKey testkey")

    apiKey, err := GetAPIKey(headers)
    if err != nil {
        t.Errorf("Unexpected error: %v", err)
    }

    if apiKey != "testkey" {
        t.Errorf("Expected 'testkey', got '%s'", apiKey)
    }
}

func TestGetAPIKeyNoAuthHeader(t *testing.T) {
    headers := http.Header{}

    _, err := GetAPIKey(headers)
    if err != ErrNoAuthHeaderIncluded {
        t.Errorf("Expected 'no authorization header included' error, got '%v'", err)
    }
}

func TestGetAPIKeyMalformedAuthHeader(t *testing.T) {
    headers := http.Header{}
    headers.Add("Authorization", "malformedheader")

    _, err := GetAPIKey(headers)
    if err == nil || err.Error() != "malformed authorization header" {
        t.Errorf("Expected 'malformed authorization header' error, got '%v'", err)
    }
}