package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		authHeader  string
		expected    string
		expectError bool
	}{
		{
			name:        "valid api key",
			authHeader:  "ApiKey abc123",
			expected:    "abc123",
			expectError: false,
		},
		{
			name:        "missing auth header",
			authHeader:  "",
			expected:    "",
			expectError: true,
		},
		{
			name:        "wrong scheme",
			authHeader:  "Bearer abc123",
			expected:    "",
			expectError: true,
		},
		{
			name:        "missing token",
			authHeader:  "ApiKey",
			expected:    "",
			expectError: true,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			headers := http.Header{}
			if tc.authHeader != "" {
				headers.Set("Authorization", tc.authHeader)
			}

			result, err := GetAPIKey(headers)

			if tc.expectError && err == nil {
				t.Errorf("expected an error but got none")
			}
			if !tc.expectError && err != nil {
				t.Errorf("unexpected error: %v", err)
			}
			if result != tc.expected {
				t.Errorf("expected %q, got %q", tc.expected, result)
			}
		})
	}
}
