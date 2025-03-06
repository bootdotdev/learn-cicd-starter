package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		header string
		apiKey string
		result string
	}{
		{"Authorization", "ApiKey 1234567890", "1234567890"}, // Valid API Key
		{"Authorization", "invalid-api-key", ""},             // Invalid API Key
		{"Authorization", "", ""},                            // Missing API Key
		{"", "ApiKey 1234567890", ""},                        // Missing Header
		{"", "", ""},                                         // Missing Header
	}

	for _, tt := range tests {
		t.Run(tt.header+tt.apiKey, func(t *testing.T) {
			// Create test http request
			req, err := http.NewRequest("GET", "/users", nil)
			if err != nil {
				t.Fatal(err)
			}

			// Add API Key to http request header
			req.Header.Set(tt.header, tt.apiKey)

			// Test GetAPIKey function
			key, err := GetAPIKey(req.Header)

			// Check returned API Key
			if key != tt.result {
				t.Errorf("Expected status '%v', got '%v'", tt.result, key)
			}
		})
	}
}
