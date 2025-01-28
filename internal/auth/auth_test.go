package auth

import (
    "net/http"
    "testing"
)

func TestGetAPIKey(t *testing.T) {
    // Mock a valid Authorization header
    header := http.Header{}
    header.Set("Authorization", "ApiKey valid-test-api-key")

    // Call the GetAPIKey function
    apiKey, err := GetAPIKey(header)

    // Check for errors
    if err != nil {
        t.Errorf("GetAPIKey() returned an error: %v", err)
    }

    // Validate the returned API key
    expected := "valid-test-api-key" // Update this to match the API key in the header
    if apiKey != expected {
        t.Errorf("GetAPIKey() = %v; want %v", apiKey, expected)
    }
}

func TestGetAPIKeyNoHeader(t *testing.T) {
    // Mock a header with no Authorization field
    header := http.Header{}

    // Call the GetAPIKey function
    _, err := GetAPIKey(header)

    // Check for the expected error
    if err != ErrNoAuthHeaderIncluded {
        t.Errorf("GetAPIKey() error = %v; want %v", err, ErrNoAuthHeaderIncluded)
    }
}

func TestGetAPIKeyMalformedHeader(t *testing.T) {
    // Mock a malformed Authorization header
    header := http.Header{}
    header.Set("Authorization", "Bearer malformed-header")

    // Call the GetAPIKey function
    _, err := GetAPIKey(header)

    // Check for the expected error
    if err == nil || err.Error() != "malformed authorization header" {
        t.Errorf("GetAPIKey() error = %v; want malformed authorization header", err)
    }
}
