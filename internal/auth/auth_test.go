package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		expected  string
		expectErr error
	}{
		{
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			expected:  "my-secret-key",
			expectErr: nil,
		},
		{
			name:      "Missing Authorization header",
			headers:   http.Header{},
			expected:  "",
			expectErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization header (missing ApiKey prefix)",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-key"},
			},
			expected:  "",
			expectErr: errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Authorization header (missing API key)",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expected:  "",
			expectErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if apiKey != tt.expected {
				t.Errorf("expected API key %q, got %q", tt.expected, apiKey)
			}
			if err != nil && tt.expectErr == nil {
				t.Errorf("unexpected error: %v", err)
			}
			if err == nil && tt.expectErr != nil {
				t.Errorf("expected error %v, got none", tt.expectErr)
			}
			if err != nil && tt.expectErr != nil && err.Error() != tt.expectErr.Error() {
				t.Errorf("expected error %v, got %v", tt.expectErr, err)
			}
		})
	}
}
