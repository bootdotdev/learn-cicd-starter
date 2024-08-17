package auth

import (
	"net/http"
	"testing"
)

// Test the GetApiKey function
func TestGetApiKey(t *testing.T) {
	// Create a mock request with an API key in the Authorization header
	req, err := http.NewRequest("GET", "/test", nil)
	if err != nil {
		t.Fatal(err)
	}
	req.Header.Set("Authorization", "ApiKey abc123")

	// Call the GetApiKey function
	apiKey, err := GetAPIKey(req.Header)
	if err != nil {
		t.Fatal(err)
	}

	// Check that the API key is correct
	if apiKey != "abc123" {
		t.Errorf("Expected API key to be 'abc123', got %s", apiKey)
	}
}
