package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectError bool
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey 123456789"},
			},
			expectedKey: "123456789",
			expectError: false,
		},
		{
			name:        "No Authorization Header",
			headers:     http.Header{},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "Malformed Header (Missing ApiKey Part)",
			headers: http.Header{
				"Authorization": []string{"Bearer 123456789"},
			},
			expectedKey: "",
			expectError: true,
		},
	}

	for _, testCase := range tests {
		t.Run(testCase.name, func(t *testing.T) {
			// Call the function we are testing
			gotKey, gotErr := GetAPIKey(testCase.headers)

			// Check if we expected an error but didn't get one (or vice versa)
			if (gotErr != nil) != testCase.expectError {
				t.Fatalf("expected error: %v, got error: %v", testCase.expectError, gotErr)
			}

			// Check if the returned key matches our expectation
			if gotKey != testCase.expectedKey {
				t.Fatalf("expected key: %v, got: %v", testCase.expectedKey, gotKey)
			}
		})
	}
}
