package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Define the test cases
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "Valid ApiKey Header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-token-123"},
			},
			expectedKey:   "my-secret-token-123",
			expectedError: nil,
		},
		{
			name:          "Missing Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Missing ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-token-123"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Header - Just the prefix",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	// Run the test cases
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tt.headers)

			// Check if the returned key matches
			if gotKey != tt.expectedKey {
				t.Errorf("GetAPIKey() gotKey = %v, want %v", gotKey, tt.expectedKey)
			}

			// Check if the error message matches
			if (gotErr == nil && tt.expectedError != nil) || (gotErr != nil && tt.expectedError == nil) {
				t.Fatalf("GetAPIKey() gotErr = %v, want %v", gotErr, tt.expectedError)
			}

			if gotErr != nil && tt.expectedError != nil && gotErr.Error() != tt.expectedError.Error() {
				t.Errorf("GetAPIKey() gotErr msg = %v, want %v", gotErr.Error(), tt.expectedError.Error())
			}
		})
	}
}
