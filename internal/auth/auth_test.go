package auth

import (
    "net/http"
    "testing"
)

// Func Tests
func TestGetAPIKey_Success(t *testing.T) {
    headers := http.Header{}
    expectedKey := "test_api_key"
    headers.Set("Authorization", "ApiKey "+expectedKey)

    key, err := GetAPIKey(headers)
    if err != nil {
        t.Fatalf("Expected no error, got %v", err)
    }
    if key != expectedKey {
        t.Errorf("Expected API key %s, got %s", expectedKey, key)
    }
}

func TestGetAPIKey_MissingAuthHeader(t *testing.T) {
    headers := http.Header{}
    _, err := GetAPIKey(headers)
    if err != ErrNoAuthHeaderIncluded {
        t.Errorf("Expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
    }
}

func TestGetAPIKey_MalformedAuthHeader(t *testing.T) { 
    headers := http.Header{}
    headers.Set("Authorization", "Bearer some_other_key")
    _, err := GetAPIKey(headers)
    if err == nil || err.Error() != "malformed authorization header" {
        t.Errorf("Expecteed 'malfrmed authorization header' error, got %v", err)
    }
}

