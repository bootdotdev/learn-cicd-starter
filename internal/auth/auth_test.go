package auth

import (
    "testing"
    "net/http"
)

func TestGetAPIKey(t *testing.T) {
    headers := make(http.Header)

    // Case 1: No auth header included
    apiKey, err := GetAPIKey(headers)
    if err != ErrNoAuthHeaderIncluded {
        t.Errorf("Expected error: %v, but got: %v", ErrNoAuthHeaderIncluded, err)
    }
    if apiKey != "" {
        t.Errorf("Expected empty API key, but got %s", apiKey)
    }

    // Case 2: Malformed auth header
    headers.Set("Authorization", "Bearer token")
    apiKey, err = GetAPIKey(headers)
    expectedErr := "malformed authorization header"
    if err.Error() != expectedErr {
        t.Errorf("Expected error: %s, but got: %v", expectedErr, err)
    }
    if apiKey != "" {
        t.Errorf("Expected empty API key, but got: %s", apiKey)
    }

    // Case 3: Valid auth header
    headers.Set("Authorization", "ApiKey my-api-key")
    apiKey, err = GetAPIKey(headers)
    if err != nil {
        t.Errorf("Expected no error, but got :%v", err)
    }
    expectedAPIKey := "my-api-key"
    if apiKey != expectedAPIKey {
        t.Errorf("Expected API key: %s, but got: %s", expectedAPIKey, apiKey)
    }
}
