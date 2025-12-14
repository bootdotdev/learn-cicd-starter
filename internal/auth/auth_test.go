package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Define the structure for our test cases
	tests := []struct {
		name          string      // Name of the test case
		headers       http.Header // Input headers
		expectedKey   string      // The key we expect to get back
		expectedError error       // The specific error we expect (for sentinel errors)
		errorString   string      // The error message string (for errors created on the fly)
	}{
		{
			name:          "No Authorization Header",
			headers:       http.Header{}, // Empty headers
			expectedKey:   "asdf",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Wrong Prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer my-token"},
			},
			expectedKey: "",
			errorString: "malformed authorization header",
		},
		{
			name: "Malformed Header - Missing Token",
			headers: http.Header{
				"Authorization": []string{"ApiKey"}, // Missing the actual key part
			},
			expectedKey: "",
			errorString: "malformed authorization header",
		},
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-token"},
			},
			expectedKey:   "my-secret-token",
			expectedError: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// 1. Check if the returned key matches expectation
			if gotKey != tt.expectedKey {
				t.Errorf("GetAPIKey() key = %v, want %v", gotKey, tt.expectedKey)
			}

			// 2. Check errors
			// Scenario A: We expect no error
			if tt.expectedError == nil && tt.errorString == "" {
				if err != nil {
					t.Errorf("GetAPIKey() unexpected error = %v", err)
				}
				return
			}

			// Scenario B: We expect a specific Sentinel Error (ErrNoAuthHeaderIncluded)
			if tt.expectedError != nil {
				if err != tt.expectedError {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.expectedError)
				}
				return
			}

			// Scenario C: We expect an error created with errors.New() inside the function
			// Since these are new pointers, we compare the error string, not the error object itself
			if tt.errorString != "" {
				if err == nil || err.Error() != tt.errorString {
					t.Errorf("GetAPIKey() error = %v, want error string %v", err, tt.errorString)
				}
			}
		})
	}
}

// Explanation of the Tests
// "No Authorization Header": Checks if the function correctly returns your exported variable ErrNoAuthHeaderIncluded when the map is empty.

// "Malformed Header":

// Wrong Prefix: Checks inputs like Bearer token instead of ApiKey token.

// Missing Token: Checks inputs that have the prefix but no actual key (length < 2).

// Note: Because your code generates a new error (errors.New("malformed...")) inside the function, we cannot compare it against a global variable. Instead, the test checks if the error message string matches.

// "Valid API Key": Checks the happy path where the format is correct (ApiKey <token>), ensuring it returns the token and nil error.

// How to run it
// Run this command in your terminal inside the directory:

// Bash

// go test -v