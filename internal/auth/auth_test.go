package auth

import (
	"errors"
	"net/http"
	"testing"
)

// TestGetAPIKey tests the GetAPIKey function for various header inputs.
func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "Valid Authorization Header",
			headers: http.Header{
				"Authorization": {"ApiKey valid_api_key_123"},
			},
			expectedKey:   "valid_api_key_123",
			expectedError: nil,
		},
		{
			name:          "Missing Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization Header - Missing ApiKey Prefix",
			headers: http.Header{
				"Authorization": {"Bearer invalid_api_key"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Authorization Header - Only ApiKey Without Key",
			headers: http.Header{
				"Authorization": {"ApiKey"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			// Check if the returned key matches the expected key
			if key != tt.expectedKey {
				t.Errorf("expected key: %s, got: %s", tt.expectedKey, key)
			}

			// Check if the returned error matches the expected error
			if err != nil && tt.expectedError == nil {
				t.Errorf("unexpected error: %v", err)
			}
			if err == nil && tt.expectedError != nil {
				t.Errorf("expected error: %v, got no error", tt.expectedError)
			}
			if err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error() {
				t.Errorf("expected error: %v, got: %v", tt.expectedError, err)
			}
		})
	}
}
