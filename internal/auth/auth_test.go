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
			name: "valid api key header",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			expectedKey: "abc123",
			expectError: true,
		},
		{
			name: "missing authorization header",
			headers: http.Header{
				"Content-Type": []string{"application/json"},
			},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "malformed authorization header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "malformed authorization header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedKey: "",
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.expectError {
				if err == nil {
					t.Errorf("Expected error but got none")
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v", err)
				}
				if key != tt.expectedKey {
					t.Errorf("Expected key %s, got %s", tt.expectedKey, key)
				}
			}
		})
	}
}
