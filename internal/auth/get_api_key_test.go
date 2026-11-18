package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Create headers with a correct Authorization header
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey my-secret-key")

	// Call the function we're testing
	apiKey, err := GetAPIKey(headers)

	// We expect NO error for a valid header
	if err != nil {
		t.Errorf("Expected no error, but got: %v", err)
	}

	// We expect the API key to be "my-secret-key"
	if apiKey != "my-secret-key" {
		t.Errorf("Expected 'my-secret-key', but got: %s", apiKey)
	}
	headers2 := http.Header{}
	// Call the function we're testing
	apiKey2, err2 := GetAPIKey(headers2)
	// We expect an error for missing header
	if err2 == nil {
		t.Errorf("Expected an error for missing header, but got none")
	}
	if apiKey2 != "" {
		t.Errorf("Expected empty API key for missing header, but got: %s", apiKey2)
	}

}
