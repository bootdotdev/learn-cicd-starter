package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test Case 1: Valid API Key in Authorization Header
	headers := http.Header{
		"Authorization": []string{"ApiKey my-api-key"},
	}

	apiKey, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("Test case 1: Expected no error, but got an error: %v", err)
	}

	if apiKey != "my-api-key" {
		t.Errorf("Test case 1: Expected API key 'my-api-key', but got '%s'", apiKey)
	}

	// Test Case 2: Missing Authorization Header
	headers = http.Header{}

	_, err = GetAPIKey(headers)
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("Test case 2: Expected error 'ErrNoAuthHeaderIncluded', but got: %v", err)
	}

	// Test Case 3: Malformed Authorization Header
	headers = http.Header{
		"Authorization": []string{"Bearer invalid-token"},
	}

	_, err = GetAPIKey(headers)
	expectedError := errors.New("malformed authorization header")
	if err == nil || err.Error() != expectedError.Error() {
		t.Errorf("Test case 3: Expected error '%v', but got: %v", expectedError, err)
	}
}
