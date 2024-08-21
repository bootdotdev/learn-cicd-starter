package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

var ErrNoAuthHeaderIncluded1 = errors.New("authorization header not included")

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectError bool
		errorMsg    string
	}{
		{
			name:        "Valid ApiKey in Authorization header",
			headers:     http.Header{"Authorization": []string{"ApiKey abc123"}},
			expectedKey: "abc123",
			expectError: false,
		},
		{
			name:        "Missing Authorization header",
			headers:     http.Header{},
			expectError: true,
			errorMsg:    "authorization header not included",
		},
		{
			name:        "Empty Authorization header",
			headers:     http.Header{"Authorization": []string{""}},
			expectError: true,
			errorMsg:    "authorization header not included",
		},
		{
			name:        "Malformed Authorization header",
			headers:     http.Header{"Authorization": []string{"Bearer abc123"}},
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
		{
			name:        "Incomplete Authorization header",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			expectError: true,
			errorMsg:    "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if tt.expectError {
				if err == nil || !strings.Contains(err.Error(), tt.errorMsg) {
					t.Errorf("expected error '%s', got '%v'", tt.errorMsg, err)
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
				}
				if apiKey != tt.expectedKey {
					t.Errorf("expected API key '%s', got '%s'", tt.expectedKey, apiKey)
				}
			}
		})
	}
}
