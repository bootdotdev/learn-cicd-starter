package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Test cases
	testCases := []struct {
		name           string
		headers        http.Header
		expectedKey    string
		expectedError  error
		errorSubstring string
	}{
		{
			name:          "Valid API Key",
			headers:       http.Header{"Authorization": []string{"ApiKey test-api-key"}},
			expectedKey:   "test-api-key",
			expectedError: nil,
		},
		{
			name:           "No Authorization Header",
			headers:        http.Header{},
			expectedKey:    "",
			expectedError:  ErrNoAuthHeaderIncluded,
			errorSubstring: "no authorization header included",
		},
		{
			name:           "Malformed Header Without ApiKey Prefix",
			headers:        http.Header{"Authorization": []string{"Bearer some-token"}},
			expectedKey:    "",
			errorSubstring: "malformed authorization header",
		},
		{
			name:           "Malformed Header Without Value",
			headers:        http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:    "",
			errorSubstring: "malformed authorization header",
		},
	}

	// Run test cases
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)

			// Check if key matches expected
			if key != tc.expectedKey {
				t.Errorf("expected key %q, got %q", tc.expectedKey, key)
			}

			// Check error conditions
			if tc.expectedError != nil && err != tc.expectedError {
				t.Errorf("expected specific error %v, got %v", tc.expectedError, err)
			}

			if tc.errorSubstring != "" && (err == nil || !contains(err.Error(), tc.errorSubstring)) {
				t.Errorf("expected error containing %q, got %v", tc.errorSubstring, err)
			}
		})
	}
}

// Helper function to check if a string contains a substring
func contains(s, substr string) bool {
	return strings.Contains(s, substr)
}
