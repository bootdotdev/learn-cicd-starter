package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expected    string
		expectError bool
	}{
		{
			name:        "no authorization header",
			headers:     http.Header{},
			expected:    "",
			expectError: true,
		},
		{
			name:        "valid api key",
			headers:     http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			expected:    "my-secret-key",
			expectError: false,
		},
		{
			name:        "malformed header missing key",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			expected:    "",
			expectError: true,
		},
		{
			name:        "malformed header wrong scheme",
			headers:     http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			expected:    "",
			expectError: true,
		},
	}

	for _, Tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if tt.expectError && err == nil {
				t.Errorf("expected error but got none")
			}
			if !tt.expectError && err != nil {
				t.Errorf("unexpected error: %v", err)
			}
			if got != tt.expected {
				t.Errorf("expected %q, got %q", tt.expected, got)
			}
		})
	}
}
