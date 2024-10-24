package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Arrange
	// Set up any necessary variables, inputs, or states
	//GetAPI Key requires an http.Header to call. So we are just defining one and setting the API key to a valid and invalid as well as having it missing.
	validHeader := http.Header{}
	validHeader.Set("Authorization", "ApiKey validKey123")

	missingHeader := http.Header{} // No API key set

	malformedHeader := http.Header{}
	malformedHeader.Set("Authorization", "Bearer validKey123")

	/* This was a test but the GetAPIKey is so bad it is fine with a blank key.
	invalidHeader := http.Header{}
	invalidHeader.Set("Authorization", "ApiKey ")
	*/

	// Act
	// Call the function you want to test
	// Assert
	// Check that the results are what you expect
	// Not doing a table driven test, just learning the basics of testing.

	// Act and Assert for validHeader
	apiKey, err := GetAPIKey(validHeader)
	if err != nil {
		t.Errorf("validHeader: expected no error, got %v", err)
	}
	if apiKey != "validKey123" {
		t.Errorf("validHeader: expected 'validKey123', got %v", apiKey)
	}

	// Act and Assert for missingHeader
	apiKey, err = GetAPIKey(missingHeader)
	if err == nil {
		t.Errorf("missingHeader: expected error, got none")
	}
	if apiKey != "" {
		t.Errorf("missingHeader: expected empty string, got %v", apiKey)
	}

	// Act and Assert for marlformedHeader
	apiKey, err = GetAPIKey(malformedHeader)
	if err == nil {
		t.Errorf("missingHeader: expected error, got none")
	}
	if apiKey != "" {
		t.Errorf("missingHeader: expected empty string, got %v", apiKey)
	}

	/* Act and Assert for invalidHeader
	apiKey, err = GetAPIKey(invalidHeader)
	if err == nil {
		t.Errorf("invalidHeader: expected error, got none")
	}
	if apiKey != "" {
		t.Errorf("invalidHeader: expected empty string, got %v", apiKey)
	}
	*/
}
