package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey test-api-key-123"},
			},
			expectedKey:   "test-api-key-123",
			expectedError: nil,
		},
		{
			name:          "No Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization Header - Missing ApiKey prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer test-token"},
			},
			expectedKey:   "",
			expectedError: nil, // Will check error message instead
		},
		{
			name: "Malformed Authorization Header - No space",
			headers: http.Header{
				"Authorization": []string{"ApiKeytest-api-key"},
			},
			expectedKey:   "",
			expectedError: nil, // Will check error message instead
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if key != tt.expectedKey {
				t.Errorf("Expected key %q, got %q", tt.expectedKey, key)
			}

			if tt.expectedError != nil {
				if err != tt.expectedError {
					t.Errorf("Expected error %v, got %v", tt.expectedError, err)
				}
			} else if tt.name != "Valid API Key" {
				// For malformed header tests, just check that an error occurred
				if err == nil {
					t.Errorf("Expected an error for malformed header, got nil")
				}
			}
		})
	}
}
