package auth

import (
	"errors"
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
			name:          "Valid API Key",
			headers:       http.Header{"Authorization": {"ApiKey abc123"}},
			expectedKey:   "abc123",
			expectedError: nil,
		},
		{
			name:          "Missing Authorization Header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded, // Use the variable from auth.go
		},
		{
			name:          "Malformed Authorization Header",
			headers:       http.Header{"Authorization": {"Bearer abc123"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Empty Authorization Header",
			headers:       http.Header{"Authorization": {""}},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded, // Adjusted to match function behavior
		},
		{
			name:          "Invalid Authorization Format",
			headers:       http.Header{"Authorization": {"ApiKey"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if apiKey != tt.expectedKey {
				t.Errorf("expected key: %v, got: %v", tt.expectedKey, apiKey)
			}
			if err != nil && tt.expectedError != nil && err.Error() != tt.expectedError.Error() {
				t.Errorf("expected error: %v, got: %v", tt.expectedError, err)
			} else if err == nil && tt.expectedError != nil {
				t.Errorf("expected error: %v, got no error", tt.expectedError)
			} else if err != nil && tt.expectedError == nil {
				t.Errorf("expected no error, got: %v", err)
			}
		})
	}
}
