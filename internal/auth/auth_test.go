package auth

import (
	"net/http"
	"testing"
)

// Test GetAPIKey
func TestGetAPIKey(t *testing.T) {
	// Test case 1: No Authorization header
	headers := http.Header{}
	headers.Add("Authorization", "Bearer somekey") // Add a header to break code
	_, err := GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected error %v, got %v", ErrNoAuthHeaderIncluded, err)
	}

	// Test case 2: Malformed Authorization header
	headers.Add("Authorization", "Bearer somekey")
	_, err = GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("expected error 'malformed authorization header', got %v", err)
	}

	// Test case 3: Correct Authorization header
	headers.Set("Authorization", "ApiKey somekey")
	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("expected no error, got %v", err)
	}
	if apiKey != "somekey" {
		t.Errorf("expected apiKey 'somekey', got %v", apiKey)
	}
}
