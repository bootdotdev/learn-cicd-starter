package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test case 1: Valid API key
	apiKey := "my-api-key"
	header := make(map[string][]string)
	header["Authorization"] = []string{"ApiKey " + apiKey}
	expected := apiKey
	result, _ := GetAPIKey(header)

	if result != expected {
		t.Errorf("Expected API key: %s, but got: %s", expected, result)
	}

	// Test case 2: Empty API key
	apiKey = ""
	expected = apiKey
	header["Authorization"] = []string{"ApiKey"}
	_, err := GetAPIKey(header)

	if err == nil {
		t.Errorf("Expected error, but got nil")
	}

	if err.Error() != "malformed authorization header" {
		t.Errorf("Expected error: Malformed authorization header, but got: %s", err.Error())
	}
}
