package main

import (
	"os"
	"testing"
)

// Function to retrieve API key
func getAPIKey() string {
	return os.Getenv("API_KEY")
}

// Unit test
func TestGetAPIKey(t *testing.T) {
	// Set up a known API key for testing
	expectedKey := "123456"
	os.Setenv("API_KEY", expectedKey)

	// Call the function to test
	actualKey := getAPIKey()

	// Check if the actual key matches the expected key
	if actualKey != expectedKey {
		t.Errorf("getAPIKey() failed, expected %v, got %v", expectedKey, actualKey)
	}
}