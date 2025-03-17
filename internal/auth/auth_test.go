package auth

import (
	"net/http"
	"testing"
)

// TestGetAPIKey tests the GetAPIKey function with various scenarios.
func TestGetAPIKey(t *testing.T) {
	// Test case 1: Valid Authorization header
	t.Log("Test Case 1: Valid Authorization header")
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-valid-api-key")

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if apiKey != "my-valid-api-key" {
		t.Errorf("Expected 'my-valid-api-key', got '%s'", apiKey)
	} else {
		t.Log("Test Case 1 passed")
	}

	// Test case 2: Missing Authorization header
	t.Log("Test Case 2: Missing Authorization header")
	headers = http.Header{} // Reset headers to simulate no Authorization header

	_, err = GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Expected error '%v', got '%v'", ErrNoAuthHeaderIncluded, err)
	} else {
		t.Log("Test Case 2 passed")
	}

	// Test case 3: Malformed Authorization header - missing 'ApiKey' prefix
	t.Log("Test Case 3: Malformed Authorization header - missing 'ApiKey' prefix")
	headers.Set("Authorization", "Bearer my-valid-api-key") // Use a different scheme

	_, err = GetAPIKey(headers)
	if err == nil || err.Error() != "malformed authorization header" {
		t.Errorf("Expected error 'malformed authorization header', got '%v'", err)
	} else {
		t.Log("Test Case 3 passed")
	}
}
